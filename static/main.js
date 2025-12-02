
      // Draggable summary logic
      (function() {
        const summary = document.getElementById('draggable-summary');
        const handle = document.getElementById('dragHandle');
        let offsetX = 0, offsetY = 0, isDragging = false;
        let lastX = null, lastY = null;
        let animationFrame = null;

        // Add smooth transition for position changes
        summary.style.transition = 'left 0.18s cubic-bezier(.4,0,.2,1), top 0.18s cubic-bezier(.4,0,.2,1)';

        function moveSummary(x, y) {
          summary.style.left = x + 'px';
          summary.style.top = y + 'px';
          summary.style.right = 'auto';
          summary.style.bottom = 'auto';
        }

        function animateMove(x, y) {
          if (animationFrame) cancelAnimationFrame(animationFrame);
          animationFrame = requestAnimationFrame(() => moveSummary(x, y));
        }

        handle.addEventListener('mousedown', function(e) {
          isDragging = true;
          offsetX = e.clientX - summary.getBoundingClientRect().left;
          offsetY = e.clientY - summary.getBoundingClientRect().top;
          summary.style.transition = 'none';
        });

        document.addEventListener('mousemove', function(e) {
          if (!isDragging) return;
          lastX = e.clientX - offsetX;
          lastY = e.clientY - offsetY;
          animateMove(lastX, lastY);
        });

        document.addEventListener('mouseup', function() {
          if (isDragging) {
            summary.style.transition = 'left 0.18s cubic-bezier(.4,0,.2,1), top 0.18s cubic-bezier(.4,0,.2,1)';
          }
          isDragging = false;
        });

        // Touch support
        handle.addEventListener('touchstart', function(e) {
          isDragging = true;
          const touch = e.touches[0];
          // Cache bounding rect once for performance
          const rect = summary.getBoundingClientRect();
          offsetX = touch.clientX - rect.left;
          offsetY = touch.clientY - rect.top;
          summary.style.transition = 'none';
        }, { passive: true });

        // Throttle touchmove for better mobile performance
        let lastTouchMove = 0;
        document.addEventListener('touchmove', function(e) {
          if (!isDragging) return;
          const now = Date.now();
          if (now - lastTouchMove < 16) return; // ~60fps
          lastTouchMove = now;
          const touch = e.touches[0];
          lastX = touch.clientX - offsetX;
          lastY = touch.clientY - offsetY;
          animateMove(lastX, lastY);
        }, { passive: false });

        document.addEventListener('touchend', function() {
          if (isDragging) {
            summary.style.transition = 'left 0.18s cubic-bezier(.4,0,.2,1), top 0.18s cubic-bezier(.4,0,.2,1)';
          }
          isDragging = false;
        }, { passive: true });
      })();
      // Basic seat selection logic (static replica)
      const seats = document.querySelectorAll(".seat");
      const selectedListEl = document.getElementById("selected-list");
      const confirmBtn = document.getElementById("confirmBtn");
      const clearBtn = document.getElementById("clearBtn");

      const MAX_SELECT = 6; // optional: max seats allowed to select

      function getSelected() {
        return Array.from(document.querySelectorAll(".seat.selected")).map(
          (s) => s.dataset.id
        );
      }
      function updateSummary() {
        const list = getSelected();
        selectedListEl.textContent = list.length ? list.join(", ") : "None";
      }

      seats.forEach((s) => {
        s.addEventListener("click", () => {
          if (s.classList.contains("reserved")) return; // cannot select reserved
          if (s.classList.contains("selected")) {
            s.classList.remove("selected");
            updateSummary();
            return;
          }
          const current = getSelected();
          if (current.length >= MAX_SELECT) {
            // simple feedback
            alert("You can select up to " + MAX_SELECT + " seats.");
            return;
          }
          s.classList.add("selected");
          updateSummary();
        });
      });

      confirmBtn.addEventListener("click", () => {
        const picked = getSelected();
        if (!picked.length) {
          alert("Please select at least one seat.");
          return;
        }
        // For now, just show a simple confirmation. In real app, you'd send to server.
        alert("Confirmed seats: " + picked.join(", "));
      });

      clearBtn.addEventListener("click", () => {
        document
          .querySelectorAll(".seat.selected")
          .forEach((s) => s.classList.remove("selected"));
        updateSummary();
      });

      // initial update
      updateSummary();
    
