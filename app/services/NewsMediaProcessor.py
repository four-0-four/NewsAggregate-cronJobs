import cv2
import numpy as np
import requests
import os
import textwrap
from moviepy.editor import ImageClip, concatenate_videoclips, AudioFileClip


def create_video_with_music(image_paths, output_video_path, music_path, duration_per_image=4, fps=24, volume_factor=0.3):
    """
    Creates a video from a list of images with background music.

    :param image_paths: List of paths to images.
    :param output_video_path: Path to save the output video.
    :param music_path: Path to the background music file.
    :param duration_per_image: Duration to display each image in seconds.
    :param fps: Frames per second for the video.
    :param volume_factor: Factor to adjust the volume of the music. Default is 0.5 (50% of the original volume).
    """
    # Create a clip for each image
    clips = [ImageClip(img_path).set_duration(duration_per_image) for img_path in image_paths]

    # Create a transition between each clip
    transition_duration = 1  # Duration of the crossfade transition in seconds
    clips_with_transition = [clips[0]]
    for clip in clips[1:]:
        clips_with_transition.append(clip.crossfadein(transition_duration))

    # Concatenate clips with crossfade transition
    video_clip = concatenate_videoclips(clips_with_transition, method="compose")

    # Set fps for the clip
    video_clip.fps = fps

    # Load and add the audio
    audio_clip = AudioFileClip(music_path).volumex(volume_factor)
    audio_duration = video_clip.duration
    audio_clip = audio_clip.set_duration(audio_duration)
    final_clip = video_clip.set_audio(audio_clip)

    # Write the result to a file
    final_clip.write_videofile(output_video_path, codec='libx264', audio_codec='aac', fps=fps)
    return final_clip

class NewsMediaProcessor:
    def __init__(self, image_url, title, local_image_path):
        self.image_url = image_url
        self.title = title
        self.local_image_path = local_image_path  # Temporary local path


    def download_image(self):
        """Download an image from a URL."""
        response = requests.get(self.image_url)
        if response.status_code == 200:
            with open(self.local_image_path, 'wb') as f:
                f.write(response.content)
            return True
        return False


    def crop_to_square(self, image):
        """Crop an image to a square using OpenCV."""
        height, width = image.shape[:2]
        new_size = min(width, height)
        top = (height - new_size) // 2
        left = (width - new_size) // 2
        return image[top:top+new_size, left:left+new_size]

    def add_title(self, image):
        """Add title with black rectangle to the bottom of an image using OpenCV."""
        # Font settings
        font = cv2.FONT_HERSHEY_COMPLEX
        font_thickness = 2
        text_color = (255, 255, 255)  # White color for contrast
        rectangle_bgr = (0, 0, 0)  # Black color
        padding = 20  # Padding around text
        image_width, image_height = image.shape[1], image.shape[0]

        # Initial font scale
        font_scale = 0.6  # Start with a smaller font scale

        # Calculate rectangle size (30% of the image height)
        rect_height = int(image_height * 0.3)
        rect_top_y = image_height - rect_height

        # Adjust font scale based on image width
        max_text_width = image_width - 2 * padding
        test_string = "W" * 40  # Test string to estimate maximum width
        while cv2.getTextSize(test_string, font, font_scale, font_thickness)[0][0] > max_text_width:
            font_scale -= 0.05

        # Increase the final font scale by 20%
        font_scale *= 1.9

        # Wrap text to fit within the rectangle
        wrapped_text = textwrap.wrap(self.title, width=30)  # Adjust the width based on your needs

        # Calculate total height of text block
        text_block_height = sum(
            [cv2.getTextSize(line, font, font_scale, font_thickness)[0][1] + padding for line in wrapped_text])

        # Starting Y-coordinate to center text block in the rectangle
        y_offset = rect_top_y + (rect_height - text_block_height) // 2

        # Draw rectangle
        cv2.rectangle(image, (0, rect_top_y), (image_width, image_height), rectangle_bgr, cv2.FILLED)

        # Add each line of text
        for line in wrapped_text:
            (text_width, text_height), _ = cv2.getTextSize(line, font, font_scale, font_thickness)
            text_x = (image_width - text_width) // 2
            if y_offset + text_height <= rect_top_y + rect_height - padding:  # Ensure text does not go beyond rectangle
                cv2.putText(image, line, (text_x, y_offset + text_height), font, font_scale, text_color, font_thickness)
                y_offset += text_height + padding

        return image

    def process_image(self):
        """Process the image: download, crop to square, add title."""
        try:
            # Download the image
            if not self.download_image():
                return "Failed to download the image"

            # Read the image using OpenCV
            img = cv2.imread(self.local_image_path)

            # Crop image to square and add title
            img = self.crop_to_square(img)
            img = self.add_title(img)

            # Save the processed image
            processed_image_path = self.local_image_path
            cv2.imwrite(processed_image_path, img)

            return processed_image_path
        except Exception as e:
            return str(e)
        #finally:
            # Clean up: delete the temporary image file
            #if os.path.exists(self.local_image_path):
            #    os.remove(self.local_image_path)