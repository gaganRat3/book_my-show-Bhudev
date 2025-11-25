# TODO for Canvas-based Seat Layout with Zoom and Pan

1. Add a canvas element inside the seat selection container in templates/seat.html.
2. Hide the existing seat div layout to avoid duplication of seat visuals.
3. Write JavaScript code in seat.html to:
   - Extract seat data from existing seat divs, including seat IDs, row labels, seat numbers, and color classes.
   - Calculate seat positions on the canvas to replicate the current seat layout design.
   - Render seats on the canvas as colored circles with seat numbers inside.
   - Implement zoom (mouse wheel) and pan (click-drag) functionality on the canvas.
   - Add click event detection on canvas seats for selection/deselection.
4. Update the seat selection summary popup to show selected seats from the canvas-based selection.
5. Ensure existing booking and seat blocking functionality integrates and works correctly with canvas seat selection.
6. Test all functionality (zoom, pan, selection, booking) for usability and consistency with the original design.
