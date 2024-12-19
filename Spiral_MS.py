import c4d
import math

def main() -> c4d.BaseObject:
    """
    Creates a perfect spiral spline that matches exactly with a circle when viewed from top.
    Starts exactly from (0,0,0) and maintains perfect circular shape throughout.
    """

    # Parameters
    start_radius = 0.0        # Starting radius at center
    end_radius = 100.0        # Final radius
    rotations = 3.0           # Number of complete rotations
    point_count = 360         # One point per degree for perfect circles
    height = 200.0           # Total height

    # Create spline object
    spiral_spline = c4d.SplineObject(point_count, c4d.SPLINETYPE_BEZIER)
    spiral_spline[c4d.SPLINEOBJECT_CLOSED] = False

    points = []

    # Add first point exactly at (0,0,0)
    points.append(c4d.Vector(0, 0, 0))

    # Generate points for the spiral
    for i in range(1, point_count):
        # Calculate angle in radians
        angle = (i / (point_count - 1)) * rotations * 2.0 * math.pi

        # Calculate progress (0 to 1)
        progress = i / (point_count - 1)

        # Calculate current radius
        radius = progress * end_radius

        # Calculate coordinates
        x = radius * math.cos(angle)
        y = progress * height  # Linear height increase
        z = radius * math.sin(angle)

        points.append(c4d.Vector(x, y, z))

    # Set all points
    spiral_spline.SetAllPoints(points)

    # Update the spline
    spiral_spline.Message(c4d.MSG_UPDATE)

    return spiral_spline