import os
import sys

import utils
import config


def main():
    """
    Reads the csv of every frame and checks if the point in the frame
    If the point in the frame then add this frame to the frames result
    """
    if (len(sys.argv) == 1):
        frame_numbers = utils.get_all_frame_numbers(config.PATH_TO_DATA)
        diluted_frame_numbers_sorted = utils.sort_and_diluted_frame_numbers(frame_numbers, config.ITEM_DILUTION)
        image = utils.stitch_frames(diluted_frame_numbers_sorted)
        utils.save_image(os.path.join(config.PATH_TO_DATA, "stitched_frames.png"), image)
        if config.DELETE_FRAMES:
            utils.delete_frames(config.PATH_TO_DATA)
        return 0
    elif (len(sys.argv) == 2):
        try:
            utils.show_frame(sys.argv[1])
        except Exception:
            print("There is no such frame number!")
        return 0
    elif (len(sys.argv) != 4):
        print("Expected python3 main.py [x: float] [y: float] [z: float] OR python3 main.py [number_of_frame: int] OR python3 main.py")
        return -1

    expected_point = sys.argv[1:4]
    expected_point = [float(cordinate) for cordinate in expected_point]

    path = os.path.join(config.PATH_TO_DATA, config.CLOUD_POINTS_NAME)

    closest_point, frame_numbers = utils.find_closest_point_line_in_csv(path, expected_point)

    print(f"We wanted x={expected_point[0]}, y={expected_point[1]}, z={expected_point[2]} and got "
          f"x={closest_point[0]}, y={closest_point[1]}, z={closest_point[2]}")

    utils.plot_data(path, expected_point, closest_point)

    image = utils.stitch_frames(frame_numbers)
    if image is not None:
        utils.show_image(image)

    return 0


if __name__ == "__main__":
    main()
