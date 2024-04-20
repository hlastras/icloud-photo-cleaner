import sys
import os
import argparse
import getpass
from collections import deque
from threading import Thread
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow
from PyQt5.QtGui import QPixmap, QImage
from PyQt5 import QtCore
from pyicloud import PyiCloudService

class AuthenticationManager:
    def __init__(self, email, password):
        self.email = email
        self.password = password
        self.api = None

    def login(self):
        self.api = PyiCloudService(self.email, self.password)
        self.handle_two_factor_authentication()
        return self.api

    def handle_two_factor_authentication(self):
        if self.api.requires_2fa:
            print("Two-factor authentication required.")
            code = input("Enter the code you received on your device: ")
            if not self.api.validate_2fa_code(code):
                print("Failed to verify two-factor authentication code.")
                sys.exit(1)
            self.api.authenticate()
        print("Logged in to iCloud successfully.")

class AlbumManager:
    def __init__(self, api):
        self.api = api

    def get_album(self, album_name='Screenshots'):
        if not self.api:
            raise Exception("iCloud not logged in")
        album = self.api.photos.albums[album_name]
        print(f"Album '{album_name}' loaded.")
        return album

class PhotoManager:
    def __init__(self, album, preload_count=5, offset=0):
        self.album = album
        self.photo_iterator = iter(album)
        self.preload_count = preload_count
        self.preloaded_images = deque()
        self.current_photos = deque()
        self.skip_photos(offset)
        self.preload_photos()

    def skip_photos(self, offset):
        print(f"Skipping {offset} photos.")
        for _ in range(offset):
            next(self.photo_iterator)
        print("Skipped")

    def preload_photos(self):
        try:
            while len(self.preloaded_images) < self.preload_count:
                self.preload_next_photo()
        except StopIteration:
            pass

    def preload_next_photo(self):
        photo = next(self.photo_iterator)
        photo_stream = photo.download()
        data = photo_stream.raw.read()
        image = QImage()
        if image.loadFromData(data):
            self.preloaded_images.append(image)
            self.current_photos.append(photo)


class BackupManager:
    def __init__(self, save_directory):
        self.save_directory = save_directory

    def backup_photo(self, photo):
        photo_stream = photo.download()
        data = photo_stream.raw.read()
        folder_path = self.save_directory
        os.makedirs(folder_path, exist_ok=True)
        file_path = os.path.join(folder_path, photo.filename)
        with open(file_path, 'wb') as file:
            file.write(data)
        print(f"Photo backed up to {file_path}")

    def delete_photo(self, photo):
        photo.delete()
        print(f"Photo deleted from iCloud: {photo.filename}")

class PhotoViewer(QMainWindow):
    def __init__(self, photo_manager, backup_manager):
        super().__init__()
        self.photo_manager = photo_manager
        self.backup_manager = backup_manager
        self.image_label = QLabel(self)
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("iCloud Photo Viewer")
        self.image_label.resize(self.width(), self.height())
        self.show()
        self.display_current_photo()

    def display_current_photo(self):
        if self.photo_manager.preloaded_images:
            pixmap = QPixmap.fromImage(self.photo_manager.preloaded_images[0])
            self.display_image(pixmap)
            if len(self.photo_manager.preloaded_images) < self.photo_manager.preload_count:
                Thread(target=self.photo_manager.preload_photos).start()
        else:
            print("No more images in cache.")

    def display_image(self, pixmap):
        screen = QApplication.primaryScreen().size()
        max_width = int(screen.width() * 0.8)
        max_height = int(screen.height() * 0.8)
        scaled_pixmap = pixmap.scaled(max_width, max_height, QtCore.Qt.KeepAspectRatio)
        self.image_label.setPixmap(scaled_pixmap)
        self.image_label.resize(scaled_pixmap.size())
        self.resize(scaled_pixmap.size())

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Right:
            self.photo_manager.preloaded_images.popleft()
            self.photo_manager.current_photos.popleft()
            self.display_current_photo()
        elif event.key() == QtCore.Qt.Key_D:
            self.backup_and_delete_current_photo()
            self.photo_manager.preloaded_images.popleft()
            self.photo_manager.current_photos.popleft()
            self.display_current_photo()
        event.accept()

    def backup_and_delete_current_photo(self):
        if self.photo_manager.current_photos:
            current_photo = self.photo_manager.current_photos[0]
            self.backup_manager.backup_photo(current_photo)
            self.backup_manager.delete_photo(current_photo)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='iCloud Photo Viewer with Preload')
    parser.add_argument('-e', '--email', type=str, required=True, help='iCloud account email')
    parser.add_argument('-p', '--password', type=str, help='iCloud account password (will prompt if not provided)')
    parser.add_argument('-o', '--offset', type=int, default=0, help='Offset to start loading photos from')
    parser.add_argument('-a', '--album', type=str, default='All photos', help='Album to load photos from')
    parser.add_argument('-l', '--load', type=int, default=10, help='Number of photos to load into memory as buffer')
    parser.add_argument('-s', '--save-dir', type=str, default='./backup', help='Directory to save backup photos before deletion')

    args = parser.parse_args()

    if not args.password:
        args.password = getpass.getpass('Password: ')

    auth_manager = AuthenticationManager(args.email, args.password)
    api = auth_manager.login()
    album_manager = AlbumManager(api)
    album = album_manager.get_album(args.album)

    photo_manager = PhotoManager(album, preload_count=args.load, offset=args.offset)
    backup_manager = BackupManager(args.save_dir)
    app = QApplication(sys.argv)
    viewer = PhotoViewer(photo_manager, backup_manager)
    sys.exit(app.exec_())
