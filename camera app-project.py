import cv2
import threading
import tkinter as tk
from tkinter import *
from PIL import Image, ImageTk, ImageEnhance, ImageFilter, ImageDraw, ImageFont
from datetime import datetime
from tkinter import messagebox, filedialog
import geocoder
from geopy.geocoders import Nominatim
import os

# Function to get location using geocoder
def get_location():
    g = geocoder.ip('me')
    if g.ok:
        return g.latlng
    else:
        return None

# Function to get place name from coordinates
def get_place_name(lat, lon):
    geolocator = Nominatim(user_agent="camera_app")
    location = geolocator.reverse((lat, lon), exactly_one=True)
    if location:
        return location.address
    else:
        return "Location Unavailable"

# Function to create necessary tkinter widgets
def create_widgets():
    root.feedlabel = Label(root, bg="steelblue", fg="white", text="WEBCAM FEED", font=('Comic Sans MS', 20))
    root.feedlabel.grid(row=1, column=1, padx=10, pady=10, columnspan=2)

    root.cameraLabel = Label(root, bg="steelblue", borderwidth=3, relief="groove")
    root.cameraLabel.grid(row=2, column=1, padx=10, pady=10, columnspan=2)

    root.saveLocationEntry = Entry(root, width=55, textvariable=destPath)
    root.saveLocationEntry.grid(row=3, column=1, padx=10, pady=10)

    root.browseButton = Button(root, width=10, text="BROWSE", command=dest_browse)
    root.browseButton.grid(row=3, column=2, padx=10, pady=10)

    root.captureBTN = Button(root, text="CAPTURE", command=capture, bg="LIGHTBLUE", font=('Comic Sans MS', 15), width=20)
    root.captureBTN.grid(row=4, column=1, padx=10, pady=10)

    root.CAMBTN = Button(root, text="STOP CAMERA", command=stop_cam, bg="LIGHTBLUE", font=('Comic Sans MS', 15), width=13)
    root.CAMBTN.grid(row=4, column=2)

    root.galleryBTN = Button(root, text="OPEN GALLERY", command=open_gallery, bg="LIGHTBLUE", font=('Comic Sans MS', 15), width=13)
    root.galleryBTN.grid(row=5, column=1, padx=10, pady=10)

    root.previewlabel = Label(root, bg="steelblue", fg="white", text="IMAGE PREVIEW", font=('Comic Sans MS', 20))
    root.previewlabel.grid(row=1, column=4, padx=10, pady=10, columnspan=2)

    root.imageLabel = Label(root, bg="steelblue", borderwidth=3, relief="groove")
    root.imageLabel.grid(row=2, column=4, padx=10, pady=10, columnspan=2)

    root.openImageEntry = Entry(root, width=55, textvariable=imagePath)
    root.openImageEntry.grid(row=3, column=4, padx=10, pady=10)

    root.openImageButton = Button(root, width=10, text="BROWSE", command=image_browse)
    root.openImageButton.grid(row=3, column=5, padx=10, pady=10)

# Function to display webcam feed
def show_feed():
    if root.cap.isOpened():
        ret, frame = root.cap.read()
        if ret:
            frame = cv2.flip(frame, 1)
            cv2.putText(frame, datetime.now().strftime('%d/%m/%Y %H:%M:%S'), (20, 30), cv2.FONT_HERSHEY_DUPLEX, 0.5, (0, 255, 255))
            cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
            video_img = Image.fromarray(cv2image)
            imgtk = ImageTk.PhotoImage(image=video_img)
            root.cameraLabel.imgtk = imgtk
            root.cameraLabel.configure(image=imgtk)
        root.cameraLabel.after(10, show_feed)

def start_thread():
    threading.Thread(target=show_feed, daemon=True).start()

def dest_browse():
    dest_directory = filedialog.askdirectory(initialdir="YOUR DIRECTORY PATH")
    destPath.set(dest_directory)

def image_browse():
    open_directory = filedialog.askopenfilename(initialdir="YOUR DIRECTORY PATH")
    imagePath.set(open_directory)
    image_view = Image.open(open_directory)
    image_resize = image_view.resize((640, 480), Image.ANTIALIAS)
    image_display = ImageTk.PhotoImage(image_resize)
    root.imageLabel.config(image=image_display)
    root.imageLabel.photo = image_display

# Function to capture and save image
def capture():
    image_name = datetime.now().strftime('%d-%m-%Y %H-%M-%S')
    if destPath.get() != '':
        image_path = destPath.get()
    else:
        messagebox.showerror("ERROR", "NO DIRECTORY SELECTED TO STORE IMAGE!!")
        return

    img_name = image_path + '/' + image_name + ".jpg"
    ret, frame = root.cap.read()

    location = get_location()
    if location:
        lat, lon = location
        location_text = f"Lat: {lat}, Lon: {lon}"
        place_name = get_place_name(lat, lon)

        # Split the place name into two lines if it's too long
        place_name_lines = place_name.split(", ")
        place_name_line1 = ", ".join(place_name_lines[:len(place_name_lines)//2])
        place_name_line2 = ", ".join(place_name_lines[len(place_name_lines)//2:])

        cv2.putText(frame, place_name_line1, (20, 60), cv2.FONT_HERSHEY_DUPLEX, 0.5, (0, 255, 255))
        cv2.putText(frame, place_name_line2, (20, 80), cv2.FONT_HERSHEY_DUPLEX, 0.5, (0, 255, 255))
    else:
        cv2.putText(frame, "Location: Unavailable", (20, 60), cv2.FONT_HERSHEY_DUPLEX, 0.5, (0, 255, 255))

    cv2.putText(frame, datetime.now().strftime('%d/%m/%Y %H:%M:%S'), (20, 30), cv2.FONT_HERSHEY_DUPLEX, 0.5, (0, 255, 255))
    success = cv2.imwrite(img_name, frame)

    saved_image = Image.open(img_name)
    saved_image = ImageTk.PhotoImage(saved_image)
    root.imageLabel.config(image=saved_image)
    root.imageLabel.photo = saved_image

    if success:
        messagebox.showinfo("SUCCESS", "IMAGE CAPTURED AND SAVED IN " + img_name)

def stop_cam():
    root.cap.release()
    root.CAMBTN.config(text="START CAMERA", command=start_cam)
    root.cameraLabel.config(text="OFF CAM", font=('Comic Sans MS', 70))

def start_cam():
    root.cap = cv2.VideoCapture(0)
    width_1, height_1 = 640, 480
    root.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width_1)
    root.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height_1)
    root.CAMBTN.config(text="STOP CAMERA", command=stop_cam)
    root.cameraLabel.config(text="")
    start_thread()

# Function to open the gallery window
def open_gallery():
    gallery_window = Toplevel(root)
    gallery_window.title("Gallery")
    gallery_window.geometry("800x600")
    gallery_window.configure(background="white")

    def update_gallery():
        for widget in gallery_frame.winfo_children():
            widget.destroy()

        image_files = [f for f in os.listdir(destPath.get()) if f.endswith(('png', 'jpg', 'jpeg'))]
        row, col = 0, 0
        for image_file in image_files:
            image_path = os.path.join(destPath.get(), image_file)
            img = Image.open(image_path)
            img.thumbnail((100, 100))
            img = ImageTk.PhotoImage(img)
            img_label = Label(gallery_frame, image=img)
            img_label.image = img
            img_label.grid(row=row, column=col, padx=5, pady=5)
            edit_btn = Button(gallery_frame, text="Edit", command=lambda p=image_path: open_editor(p))
            edit_btn.grid(row=row + 1, column=col, padx=5, pady=5)
            del_btn = Button(gallery_frame, text="Delete", command=lambda p=image_path: delete_image(p))
            del_btn.grid(row=row + 2, column=col, padx=5, pady=5)
            col += 1
            if col == 6:
                col = 0
                row += 3

    def delete_image(image_path):
        os.remove(image_path)
        update_gallery()

    gallery_frame = Frame(gallery_window, bg="white")
    gallery_frame.pack(expand=True, fill=BOTH)
    update_gallery()

# Function to open the image editor
def open_editor(image_path):
    editor_window = Toplevel(root)
    editor_window.title("Photo Editor")
    editor_window.geometry("800x600")

    img = Image.open(image_path)
    img.thumbnail((500, 500))
    img_display = ImageTk.PhotoImage(img)
    
    editor_label = Label(editor_window, image=img_display)
    editor_label.image = img_display
    editor_label.pack()

    def apply_changes(new_img):
        nonlocal img_display
        new_img.thumbnail((500, 500))
        img_display = ImageTk.PhotoImage(new_img)
        editor_label.config(image=img_display)
        editor_label.image = img_display

    def save_changes():
        nonlocal img
        img.save(image_path)
        messagebox.showinfo("Saved", "Image saved successfully!")

    def crop_image():
        nonlocal img
        cropped_img = img.crop((50, 50, 400, 400))  # Example crop
        img = cropped_img
        apply_changes(cropped_img)

    def apply_filter():
        nonlocal img
        filtered_img = img.filter(ImageFilter.BLUR)  # Example filter
        img = filtered_img
        apply_changes(filtered_img)

    def adjust_brightness(value):
        nonlocal img
        enhancer = ImageEnhance.Brightness(img)
        bright_img = enhancer.enhance(float(value))
        apply_changes(bright_img)

    def add_text():
        nonlocal img
        draw = ImageDraw.Draw(img)
        font = ImageFont.load_default()
        draw.text((10, 10), "Sample Text", font=font, fill="white")
        apply_changes(img)

    crop_btn = Button(editor_window, text="Crop", command=crop_image)
    crop_btn.pack(side=LEFT)

    filter_btn = Button(editor_window, text="Filter", command=apply_filter)
    filter_btn.pack(side=LEFT)

    brightness_scale = Scale(editor_window, from_=0.5, to=2.0, resolution=0.1, orient=HORIZONTAL, label="Brightness", command=adjust_brightness)
    brightness_scale.set(1.0)
    brightness_scale.pack(side=LEFT)

    text_btn = Button(editor_window, text="Add Text", command=add_text)
    text_btn.pack(side=LEFT)

    save_btn = Button(editor_window, text="Save", command=save_changes)
    save_btn.pack(side=LEFT)

root = tk.Tk()
root.cap = cv2.VideoCapture(0)
width, height = 640, 480
root.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
root.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
root.title("Camera App")
root.geometry("1340x700")
root.resizable(True, True)
root.configure(background="sky blue")

destPath = StringVar()
imagePath = StringVar()

create_widgets()
start_thread()
root.mainloop()
