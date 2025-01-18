import cv2
import numpy as np

# WALL_COLOR (BGR): 167, 73, 29
WALL_COLOR = np.array([167, 73, 29])

# True = wall, False = empty space
def filter_walls(image):
    image = filter_walls_as_image(image)
    image = image.astype(dtype=bool)
    return image

# 255 = empty space, 0 = wall
def filter_walls_as_image(image):
    image = -(cv2.inRange(image, WALL_COLOR - 50, WALL_COLOR + 50).astype(dtype="uint8") - 255)
    return image

if __name__ == '__main__':
    img = cv2.imread('/Users/vincentlim/Projects/2025/path-hero/static/images/floor/hospital_simple.png')
    # img = filter_walls(img)
    img = filter_walls_as_image(img)
    # cv2.imshow("", img.astype(dtype="uint8") * 255)
    cv2.imshow("", img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
