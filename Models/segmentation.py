import cv2
import glob, os
import numpy as np
import h5py
import matplotlib.pyplot as plt

from natsort import natsorted
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from scipy.ndimage import gaussian_filter1d


DEBUG = False
G_RANGE = (0, 255, 0)
R_RANGE = (0, 0, 255)


def get_file_list(directory, extensions=['*.jpg', '*.jpeg', '*.png']):
    if not os.path.exists(directory):
        os.makedirs(directory)
    file_list = []
    for ext in extensions:
        file_list.extend(glob.glob(os.path.join(directory, ext)))
    return natsorted(file_list)


def get_image_mask(file_path):
    """Generate a mask to segment leaf regions from the background."""
    image = cv2.imread(file_path)
    if image is None:
        raise FileNotFoundError(f"Image not found: {file_path}")

    hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    # lower_hsv = np.array([25, 25, 25])
    # upper_hsv = np.array([110, 255, 190])
    lower_hsv = np.array([0, 35, 0])
    upper_hsv = np.array([360, 100, 255])

    kernel = np.ones((11, 11), dtype=np.uint8)
    mask = cv2.inRange(hsv_image, lower_hsv, upper_hsv)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

    return image, mask

    # """Generate a mask to segment leaf regions from the background, excluding the hydroponic rig frame."""
    # # Read the image from file
    # image = cv2.imread(file_path)
    # if image is None:
    #     raise FileNotFoundError(f"Image not found: {file_path}")
    #
    # # Convert the image to HSV
    # hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    #
    # # Define HSV range for leaf color (greens)
    # lower_hsv_leaf = np.array([50, 20, 40])
    # upper_hsv_leaf = np.array([70, 70, 100])
    # leaf_mask = cv2.inRange(hsv_image, lower_hsv_leaf, upper_hsv_leaf)
    #
    # # Apply morphological operations to clean up the mask
    # kernel = np.ones((25, 25), dtype=np.uint8)
    # combined_mask = cv2.morphologyEx(leaf_mask, cv2.MORPH_DILATE, kernel)
    # combined_mask = cv2.morphologyEx(leaf_mask, cv2.MORPH_DILATE, kernel)
    # combined_mask = cv2.morphologyEx(leaf_mask, cv2.MORPH_ERODE,  kernel)
    # combined_mask = cv2.morphologyEx(leaf_mask, cv2.MORPH_CLOSE,  kernel)
    # combined_mask = cv2.morphologyEx(leaf_mask, cv2.MORPH_ERODE,  kernel)
    #
    # return image, combined_mask


def extract_leaf(image, mask):
    """Extract the leaf from the image using the given mask."""
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        raise ValueError("No contours found in the mask.")

    leaf_mask = np.zeros_like(mask)
    for contour in contours:
        if cv2.contourArea(contour) > 400:
            cv2.drawContours(leaf_mask, [contour], -1, 255, thickness=cv2.FILLED)

    kernel = np.ones((5, 5), np.uint8)
    leaf_mask = cv2.morphologyEx(leaf_mask, cv2.MORPH_OPEN, kernel)
    extracted_leaf = cv2.bitwise_and(image, image, mask=leaf_mask)

    return extracted_leaf


def remove_stem(image, erosion_kernel=(5, 5), dilation_kernel=(15, 15)):
    """Remove the stem from the leaf image using erosion and dilation."""
    grayscale = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, binary_mask = cv2.threshold(grayscale, 1, 255, cv2.THRESH_BINARY)

    erosion = np.ones(erosion_kernel, np.uint8)
    dilation = np.ones(dilation_kernel, np.uint8)

    eroded_mask = cv2.erode(binary_mask, erosion, iterations=1)
    dilated_mask = cv2.dilate(eroded_mask, dilation, iterations=1)

    stemless_image = cv2.bitwise_and(image, image, mask=dilated_mask)
    return stemless_image


def calculate_waviness_and_solidity(image):
    """Calculate the waviness and solidity of the leaf in the given image."""
    image_c = image.copy()
    grayscale = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Finding the contours of the image
    _, threshold = cv2.threshold(grayscale, 0, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(threshold, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_TC89_KCOS)
    if not contours:
        raise ValueError("No contours found for waviness calculation.")

    # Approximation using polygonal curves for the contours of the image
    contour = max(contours, key=cv2.contourArea)
    epsilon = 0.01 * cv2.arcLength(contour, True)
    approx = cv2.approxPolyDP(contour, epsilon, True)

    # Solidity calculation using the contours and dividing it
    # by the hull area to see how broken or wavy edges
    hull = cv2.convexHull(contour)
    contour_area = cv2.contourArea(contour)
    hull_area = cv2.contourArea(hull)

    # approx_image is the approximated image using the polygonal curves as contours
    approx_image = cv2.drawContours(image_c, [hull], -1, G_RANGE, 8)
    approx_image = cv2.drawContours(approx_image, [approx], -1, R_RANGE, 8)
    if DEBUG:
        cv2.imshow('Contour Approximation', image_c)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    # solidity -> 1.0 implies smooth contours, while -> implies broken
    solidity = float(contour_area) / hull_area

    # Perimeter and area ratios can also be used as a secondary way of
    # learning how wavy a leaf is
    perimeter = cv2.arcLength(contour, True)
    hull_peri = cv2.arcLength(hull, True)

    # waviness -> inf implies that the contour will have more
    # irregularities vs the convex hull
    waviness = perimeter / hull_peri

    return approx_image, solidity, waviness


def get_image_histogram(image, bins=32, smooth=True, channels=3):
    histograms = []
    for i in range(channels):
        hist = cv2.calcHist([image], [i], None, [bins], [0, 256])
        hist = hist.flatten()
        if smooth: hist = gaussian_filter1d(hist, sigma=2)
        hist /= np.sum(hist)
        histograms.append(hist)

    return histograms


def rotate_image(image, angle=0):
    """Rotate the image by the specified angle."""
    (height, width) = image.shape[:2]
    center = (width // 2, height // 2)

    rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
    cos = np.abs(rotation_matrix[0, 0])
    sin = np.abs(rotation_matrix[0, 1])

    new_width = int((height * sin) + (width * cos))
    new_height = int((height * cos) + (width * sin))

    rotation_matrix[0, 2] += (new_width / 2) - center[0]
    rotation_matrix[1, 2] += (new_height / 2) - center[1]

    rotated_image = cv2.warpAffine(image, rotation_matrix, (new_width, new_height),
                                   flags=cv2.INTER_CUBIC,
                                   borderMode=cv2.BORDER_CONSTANT,
                                   borderValue=(0, 0, 0))

    return rotated_image


def save_image(filename, image, output_directory):
    """Save the processed image to the specified directory."""
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    output_filename = f"processed_{os.path.basename(filename)}"
    output_path = os.path.join(output_directory, output_filename)
    plt.imsave(output_path, image)


def process_directory(input_directory, input_folder, output_folder):
    """Process all images in the specified input directory and save them to the output directory."""
    input_path = os.path.join(input_directory, input_folder)
    output_path = os.path.join(input_directory, output_folder)
    image_files = get_file_list(input_path)

    for idx, file_path in enumerate(image_files):
        if DEBUG and idx > 10:  # Limit processing for debugging
            break

        try:
            image, mask = get_image_mask(file_path)
            leaf = extract_leaf(image, mask)

            # Repeat stem removal for additional effect
            stemless_leaf = leaf
            for _ in range(5):
                stemless_leaf = remove_stem(stemless_leaf)

            rotated_leaf = rotate_image(stemless_leaf)
            save_image(file_path, rotated_leaf, output_path)

        except (FileNotFoundError, ValueError) as e:
            print(f"Error processing {file_path}: {e}")


def create_dataset(input_directory, path_to_this_file, bins=32):
    with h5py.File(path_to_this_file, 'w') as file:
        image_files = glob.glob(os.path.join(input_directory, "*.jpg"))

        image_dataset = file.create_dataset('images', (len(image_files), 256, 256, 3), dtype=np.uint8)
        approx_dataset = file.create_dataset('approx', (len(image_files), 256, 256, 3), dtype=np.uint8)
        histogram_dataset = file.create_dataset('histogram', (len(image_files), bins * 3), dtype=np.float32)
        solidity_dataset = file.create_dataset('solidity', (len(image_files),), dtype=np.float32)
        waviness_dataset = file.create_dataset('waviness', (len(image_files),), dtype=np.float32)

        for idx, path in enumerate(image_files):
            image, mask = get_image_mask(path)
            leaf = extract_leaf(image, mask)

            stemless_leaf = remove_stem(leaf)

            resized_original = cv2.resize(image, (256, 256))
            resized = cv2.resize(stemless_leaf, (256, 256))

            # def get_image_histogram(image, bins=32, smooth=True, channels=3):
            histogram = get_image_histogram(resized, bins=bins, smooth=True)

            approx, solidity, waviness = calculate_waviness_and_solidity(stemless_leaf)
            resized_approx = cv2.resize(approx, (256, 256))

            image_dataset[idx] = resized_original
            histogram_dataset[idx] = np.asarray(histogram).flatten()
            solidity_dataset[idx] = solidity
            waviness_dataset[idx] = waviness
            approx_dataset[idx] = resized_approx


def save_image_with_ft(image, solidity, waviness, approximated, histogram, group):
    group.create_dataset('image', data=image, dtype=np.uint8)
    group.create_dataset('approx', data=approximated, dtype=np.uint8)
    group.create_dataset('histogram', data=histogram, dtype=np.float32)
    group.attrs['solidity'] = solidity
    group.attrs['waviness'] = waviness


def visualize_h5_file(path, sample_count=5):
    with h5py.File(path, 'r') as f:
        images = f['images']
        approximates = f['approx']
        histograms = f['histogram']
        solidities = f['solidity']
        wavinesses = f['waviness']

        samples = min(sample_count, len(images))
        fig, axes = plt.subplots(samples, 3, figsize=(15, 5 * samples))

        for idx in range(samples):
            print(axes.shape)
            image = images[idx]
            axes[idx, 0].imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
            axes[idx, 0].set_title(
                f'Original Leaf Image\nSolidity: {solidities[idx]:.2f}, Waviness: {wavinesses[idx]:.2f}')
            axes[idx, 0].axis('off')

            # Approximated Image
            approx_image = approximates[idx]
            axes[idx, 1].imshow(cv2.cvtColor(approx_image, cv2.COLOR_BGR2RGB))
            axes[idx, 1].set_title('Approximated Contour Image')
            axes[idx, 1].axis('off')

            # Color Histogram
            histogram = histograms[idx]
            print("histogram.shape: ", histogram.shape)
            bins = histogram.shape[0] // 3
            b_hist = histogram[:bins]
            g_hist = histogram[bins:2 * bins]
            r_hist = histogram[2 * bins:]

            axes[idx, 2].plot(b_hist, color='b', label='Blue Channel')
            axes[idx, 2].plot(g_hist, color='g', label='Green Channel')
            axes[idx, 2].plot(r_hist, color='r', label='Red Channel')
            axes[idx, 2].set_title('Color Histogram')
            axes[idx, 2].set_xlabel('Bins')
            axes[idx, 2].set_ylabel('Frequency')
            axes[idx, 2].legend()

        plt.tight_layout()
        plt.show()


def main():
    """Main function to process different leaf categories."""
    base_directory = "test_spinach/"
    categories = [("mites/", "out_mites/", "mites.h5py"), ("healthy/", "out_healthy/", "healthy.h5py"), ("spots/", "out_spots/", "spots.h5py")]

    for input_folder, output_folder, h5out in categories:
        process_directory(base_directory, input_folder, output_folder)
        directory = os.path.join(base_directory, input_folder)
        create_dataset(directory, h5out)
        visualize_h5_file(h5out)


def local():
    """Main function to process different leaf categories."""
    base_directory = "leaves/"
    #categories = [("diseased/", "out_dis/", "dis.h5py"), ("healthy/", "out_healthy/", "healthy.h5py")]
    categories = [("bgtest/", "out_bgtest/", "bg.h5py")]

    for input_folder, output_folder, h5out in categories:
        process_directory(base_directory, input_folder, output_folder)
        directory = os.path.join(base_directory, input_folder)
        create_dataset(directory, h5out)
        visualize_h5_file(h5out)


if __name__ == "__main__":
    #main()
    local()
