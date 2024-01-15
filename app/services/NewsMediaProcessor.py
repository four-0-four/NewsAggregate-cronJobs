import cv2
import numpy as np
import requests
import os
import textwrap
from moviepy.editor import ImageClip, concatenate_videoclips, AudioFileClip



def create_social_media_description(news_data):
    category = news_data['category']
    news_items = news_data['news']

    # Start of the social media post
    post = f"📰 Here's the top news in {category} in the past 6 hours, and here are the titles: \n\n"

    # Adding each news title
    for news in news_items[:5]:  # Limit to top 5 news items
        post += f"🔹 {news['title']}\n"

    # Adding hashtags from keywords
    post += "\n#️⃣ Hashtags:\n"
    unique_keywords = set()
    for news in news_items[:5]:
        for keyword in news['keywords'][:5]:  # Limit to top 5 keywords
            unique_keywords.add(keyword.replace(' ', '').replace('&', 'and'))

    post += ' '.join([f'#{keyword}' for keyword in unique_keywords])

    # Save to a text file
    with open('media/social_media_post.txt', 'w', encoding='utf-8') as file:
        file.write(post)

    return post


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
    fade_duration = 5  # Duration of the fadeout in seconds
    audio_clip = audio_clip.set_duration(audio_duration).audio_fadeout(fade_duration)
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
        # Font settings
        font = cv2.FONT_HERSHEY_COMPLEX
        font_scale = 1.1  # Increased font scale
        font_thickness = 2
        text_color = (0, 0, 0)  # Black color for text
        rectangle_bgr = (0, 255, 255)  # Yellow color for rectangle
        padding = 27  # Increased padding around text

        # Wrap text to fit within the image width
        wrapped_text = textwrap.wrap(self.title, width=27)  # Adjust width based on your needs

        # Calculate the total height of the text block
        total_text_height = sum(
            [cv2.getTextSize(line, font, font_scale, font_thickness)[0][1] + padding for line in wrapped_text])

        # Starting y position to center text block in the middle-lower part of the image
        y_offset = (image.shape[0] + total_text_height) // 2 - total_text_height + 120

        for line in wrapped_text:
            # Get text size
            text_size = cv2.getTextSize(line, font, font_scale, font_thickness)[0]

            # Calculate text and rectangle positions
            text_x = (image.shape[1] - text_size[0]) // 2
            text_y = y_offset + text_size[1] + padding // 2

            rectangle_start_point = (text_x - padding, y_offset)
            rectangle_end_point = (text_x + text_size[0] + padding, y_offset + text_size[1] + padding)

            # Draw rectangle
            cv2.rectangle(image, rectangle_start_point, rectangle_end_point, rectangle_bgr, -1)

            # Draw text
            cv2.putText(image, line, (text_x, text_y), font, font_scale, text_color, font_thickness)

            # Update y position for next line
            y_offset += text_size[1] + padding + 5

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