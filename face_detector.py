import cv2

def detect_and_extract_face(image_path):
    """
    Scans an image for human faces, draws a bounding box,
    and saves the extracted face as a new image file.
    """
    print(f"[*] Loading image: {image_path}")

    #step 1: Load the image using OpenCV
    image = cv2.imread(image_path)
    if image is None:
        print("[!] Error: Could not load image. Make sure the file exists in the folder.")
        return False
    #step 2: Convert to grayscale (works well for Haar Cascades)
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    #step 3: Load the pre-trained Haar Cascade face detection model built into OpenCV
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    #step 4: Detect faces in the image
    print("[*] Scanning for facial regions...")
    faces = face_cascade.detectMultiScale(
        gray_image,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(30, 30)
    )

    if len(faces) == 0:
        print("[!] No faces detected in the image.")
        return False

    print(f"[+] Found {len(faces)} face(s). Extracting...")

    #step 5: Loop through the detected faces
    for (x, y, w, h) in faces:
        cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
        extracted_face = image[y:y + h, x:x + w]
        cv2.imwrite("extracted_face_for_CNN.jpg", extracted_face)

        # step 6: save the image with the green bounding box and drawn on it
        cv2.imwrite("face_detection_result.jpg", image)
        print("[+] Saved 'extracted_face_for_CNN.jpg' and 'face_detection_result.jpg'")
        return True


if __name__ == "__main__":
    print("=== DeepShield: Face Detection Module ===\n")
    
    #run the detection function
    detect_and_extract_face("test_face.jpg")