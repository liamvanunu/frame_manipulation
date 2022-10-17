import os
import re
import csv
import sys
import glob

import cv2 as cv
import numpy as np
import matplotlib.pyplot as plt

import config


def _find_distance_3d(point1: list, point2: list) -> float:
    """
    Gets two point and find the distance between them
    """
    return (((point2[0] - point1[0]) ** 2) + ((point2[1] - point1[1]) ** 2) + ((point2[2] - point1[2]) ** 2)) ** (0.5)


def _extract_csv_file(path: str) -> list:
    """
    Gets path to csv file and returns the list of rows of it
    """
    rows = []
    with open(path, 'r') as csvfile:
        csvreader = csv.reader(csvfile)

        for row in csvreader:
            rows.append(row)

    return rows


def _create_point_from_line_in_csv(line: list) -> list:
    """
    Gets line of csv file and return the point in the line
    """
    return [float(cordinate) for cordinate in [line[0], line[2], line[1]]]


def _get_frames_from_line_in_csv(line: list) -> list:
    """
    Gets line of csv file and return all the frames that the point in them
    """
    return [int(cell) for cell in line[3:]]


def find_closest_point_line_in_csv(path: str, expected_point: list) -> int:
    """
    Gets point and path of the csv and returns the frames of the line that contains the closest point in the csv file
    """
    rows = _extract_csv_file(path)
    min_distance = sys.maxsize
    min_line = -1
    for line_number, line in enumerate(rows):
        point_to_check = _create_point_from_line_in_csv(line)
        distance = _find_distance_3d(point_to_check, expected_point)
        if distance < min_distance:
            min_distance = distance
            min_line = line_number

    return _create_point_from_line_in_csv(rows[min_line]), _get_frames_from_line_in_csv(rows[min_line])


def _convert_frame_numbers_to_frames_path(frame_numbers: list) -> list:
    """
    Gets the frames in numbers format and convert it to paths to files
    """
    return [os.path.join(config.PATH_TO_DATA, f"frame_{frame_number}.png") for frame_number in frame_numbers]


def stitch_frames(frame_numbers: list) -> list:
    """
    Gets from list of frames(number of frames) the stithicng of all of them
    """
    # If there is only one frame, show it
    if len(frame_numbers) == 1:
        print("only one frame, showing it...")
        frames_path = _convert_frame_numbers_to_frames_path(frame_numbers)
        cv.imshow("Frame of closest point", cv.imread(frames_path[0]))
        cv.waitKey(0)
        cv.destroyAllWindows()
        return None

    frames = []
    frames_path = _convert_frame_numbers_to_frames_path(frame_numbers)

    for frame in frames_path:
        frame = cv.imread(frame)
        if frame is None:
            print("can't read image!")
            sys.exit(-1)
        frames.append(frame)

    stitcher = cv.Stitcher.create(cv.Stitcher_PANORAMA)
    status, pano = stitcher.stitch(frames)

    if status != cv.Stitcher_OK:
        print("Can't stitch images, error code = %d" % status)
        sys.exit(-1)

    return pano


def show_image(image: list) -> None:
    """
    Get cv image and shows it
    """
    # Show the result
    cv.imshow("stitched frames", image)
    cv.waitKey(0)
    cv.destroyAllWindows()


def show_frame(frame_number: int) -> None:
    """
    Gets frame number and shows the image of it
    """
    cv.imshow(f"Frame {frame_number}", cv.imread(os.path.join(config.PATH_TO_DATA, f"frame_{frame_number}.png")))
    cv.waitKey(0)
    cv.destroyAllWindows()


def _get_all_points(rows: list) -> {list, list}:
    """
    Gets the rows of the csv file and returns two lists of x's and y's
    """
    x, y, z = [], [], []

    for row in rows:
        x.append(float(row[0]))
        y.append(float(row[2]))
        z.append(float(row[1]))
    return x, y, z


def plot_data(path: str, expected_point: list, closest_point: list) -> None:
    """
    Gets the path of the csv file, the point we wished to get and the closest point to it
    and plot the cloud points with marking the closest point and the point we wished to get
    """
    rows = _extract_csv_file(path)

    x, y, _ = _get_all_points(rows)

    # Plot all the points
    plt.scatter(np.array(x), np.array(y), color="grey", linewidth=0.1, s=2)

    # Plot the closes point in green and the wished point in red and make them big
    plt.scatter(expected_point[0], expected_point[1], color="red", linewidth=0.1, s=20)
    plt.scatter(closest_point[0], closest_point[1], color="green", linewidth=0.1, s=20)

    plt.draw()
    # Press ank key to close the plot
    while True:
        if plt.waitforbuttonpress(0):
            plt.close()
            break


def _get_all_frame_numbers(path: str) -> list:
    """
    Gets the path to the directory of the data and return all the frame numbers
    """
    frame_number_list = glob.glob(os.path.join(path, "frame_*.png"))
    frame_number_list = [os.path.basename(curr_path) for curr_path in frame_number_list]
    return [int(re.findall('[0-9]+', frame_path)[0]) for frame_path in frame_number_list]


def _sort_and_diluted_frame_numbers(frame_numbers: list, item_dilution: int) -> list:
    """
    get list and how much to dilute Sort the list and save every 20th item
    """
    frame_numbers.sort()
    diluted_frame_numbers = []
    for i in range(len(frame_numbers)):
        if i % item_dilution == 0:
            diluted_frame_numbers.append(frame_numbers[i])
    return diluted_frame_numbers


def _save_image(path_to_save: str, image: list) -> None:
    """
    Gets the path we want to save the image to and the image we want to save
    """
    cv.imwrite(path_to_save, image)


def _delete_frames(path: str) -> None:
    """
    delete all the frame images from the path of the data
    """
    frame_images_list = glob.glob(os.path.join(path, "frame_*.png"))
    for frame in frame_images_list:
        os.remove(frame)


def stitch_all_frames(path: str, item_dilution: int, delete_frames: bool) -> None:
    """
    Get path to the data folder, the item dilution amount and if to delete the frames
    and save to it all the stitched frames as an picture named stitched_frames.png
    and delete if asked for
    """
    frame_numbers = _get_all_frame_numbers(path)
    diluted_frame_numbers_sorted = _sort_and_diluted_frame_numbers(frame_numbers, item_dilution)
    image = stitch_frames(diluted_frame_numbers_sorted)
    _save_image(os.path.join(path, "stitched_frames.png"), image)
    if delete_frames:
        _delete_frames(path)


def _get_average_location(path: str) -> list:
    """
    Gets the path of the data folder and returns list
    that define the average point of the scan
    """
    number_of_frames = len(glob.glob(os.path.join(path, "frameData_*.csv")))
    average_point = [0, 0, 0]
    frames_data_list = glob.glob(os.path.join(path, "frameData_*.csv"))
    for frame_data in frames_data_list:
        row = _extract_csv_file(frame_data)[0]
        row = [float(item) for item in row]
        average_point[0] += row[1]
        average_point[1] += row[2]
        average_point[2] += row[3]
    average_point[0] /= number_of_frames
    average_point[1] /= number_of_frames
    average_point[2] /= number_of_frames
    return average_point


def _write_row_to_csv(row: list, file_path: str) -> None:
    """
    Get the file path we want to save and the row we want to save
    and save the row to this path in csv format
    """
    with open(file_path, 'w') as f:
        writer = csv.writer(f)
        writer.writerow(row)


def save_average_location(path: str) -> None:
    """
    Get the path to the data folder and save csv file
    that contains the average location at the scan
    """
    average_point = _get_average_location(path)
    _write_row_to_csv(average_point, os.path.join(path, "average_location.csv"))
