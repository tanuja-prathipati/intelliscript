# -*- coding: utf-8 -*-
"""Transcription.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1FQWEdbZuKRKpT0AJJ-o_KJsg1j1WfQYn
"""

!pip install pytube openai-whisper

!pip install youtube_transcript_api

#Final Transcription
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptAvailable, NoTranscriptFound, VideoUnavailable
from googletrans import LANGUAGES
import whisper
from pytube import YouTube
import warnings,subprocess,os

# Suppress FP16 warnings
warnings.filterwarnings("ignore", message="FP16 is not supported on CPU; using FP32 instead")

manual_subtitles=False

def eng_aliases():
    # Add aliases for English languages

    LANGUAGES['en-us']='English'
    LANGUAGES['en-US']='English'
    LANGUAGES['en-gb']='English'
    LANGUAGES['en-GB']='English'

def fetch_transcript(video_link):
    """Fetches the transcript for a given YouTube video link.

    Args:
        video_link (str): A string containing the YouTube video link.

    Returns:
        str: A string containing the video's transcript, or an error message if the transcript cannot be found or generated.
    """

    # Extract the video ID from the video_link
    video_id = video_link.split('=')[1]
    transcript=""
    eng_aliases()

    try:
        # Try to find a manually created transcript in English or American English
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        manual_transcript = transcript_list.find_manually_created_transcript(LANGUAGES.keys())
        if manual_transcript.language_code.lower() not in ['en','en-us','en-gb']:
            transcript=manual_transcript.translate('en')
        else:
            transcript = manual_transcript
        global manual_subtitles
        manual_subtitles=True

    except NoTranscriptFound:
        try:
            auto_gen_transcript= transcript_list.find_generated_transcript(LANGUAGES.keys())
            if auto_gen_transcript.language_code.lower() not in ['en','en-us','en-gb']:
                transcript=auto_gen_transcript.translate('en')
            else:
                transcript = auto_gen_transcript

        except:
            return speech_to_text(video_link)

    except VideoUnavailable:
        return "Video not found, enter a valid youtube video link."

    except (TranscriptsDisabled, NoTranscriptAvailable):
        return speech_to_text(video_link)

    except Exception as e:
        return f"An error occured during transcription."
    try:
        transcript_text = " ".join([item['text'] for item in transcript.fetch()]).replace("\n"," ")
        return transcript_text

    except Exception as e:
        return e


def speech_to_text(video_link):
    output_file = "output.web3"

    # Create a temporary directory to store the video and audio files
    temp_dir = "temp"
    os.makedirs(temp_dir, exist_ok=True)
    yt = YouTube(video_link)
    title=yt.title
    print(title)
    name=title+".mp4"
    file_location = "/content/"+temp_dir+"/"+name

    stream = yt.streams.filter(only_audio=True, file_extension="mp4").first()
    stream.download(output_path=temp_dir)
    model = whisper.load_model("base")
    result = model.transcribe(file_location)
    return (result["text"])

def main(youtube_url):
    # Check if the video has existing subtitles
    transcript = fetch_transcript(video_link)

    if transcript:
        print("Using Existing Subtitles:")
        print(transcript)
    else:
        print("No Existing Subtitles. Using ASR:")
        asr_transcript = speech_to_text(video_link)
        print(asr_transcript)

if __name__ == "__main__":
    video_link = "https://www.youtube.com/watch?v=ronG4855kCg&list=PLGtLbc4Q42PDYWYWWWw9gg7Bvt_zAdZ3I"  # Change to your desired YouTube URL
    main(video_link)

pip install nltk

pip install transformers

pip install sumy

import nltk
import os

# Set the path to the Intelliscript folder on your desktop
desktop_path = os.path.join(os.path.expanduser("~"), "Desktop", "IntelliScript")

# Create the nltk_data directory within the Intelliscript folder
nltk_data_path = os.path.join(desktop_path, "nltk_data")
if not os.path.exists(nltk_data_path):
    os.makedirs(nltk_data_path)

# Set the NLTK data path to the newly created nltk_data directory
nltk.data.path.append(nltk_data_path)

# Download the 'punkt' package
nltk.download('punkt')


from transformers import pipeline
from nltk.tokenize import sent_tokenize
from sumy.summarizers.text_rank import TextRankSummarizer
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lex_rank import LexRankSummarizer
from sumy.summarizers.lsa import LsaSummarizer
from transformers import pipeline, AutoTokenizer
import unicodedata
import logging

logging.getLogger("transformers").setLevel(logging.ERROR)

def get_summary(manual_subtitles, text, model_choice):
    if manual_subtitles:
        extractive_summary = get_extractive_summary(text)
        abstractive_summary = get_abstractive_summary(extractive_summary, model_choice)
    else:
        abstractive_summary = get_abstractive_summary(text, model_choice)

    return abstractive_summary

def get_abstractive_summary(extractive_summary, model_choice):
    models = {
        0: "facebook/bart-large-cnn",
        1: "t5-base"
    }
    model_name = models[model_choice]

    tokenizer = AutoTokenizer.from_pretrained(model_name, model_max_length=1024)  # Adjust max length as needed

    # Load the model for summarization
    generator = pipeline('summarization', model=model_name)

    # Generate abstractive summary
    abstractive_summary = generator(extractive_summary, max_length=100, min_length=5, do_sample=True, early_stopping=True)[0]['summary_text']

    return abstractive_summary

def get_extractive_summary(text):
    parser = PlaintextParser.from_string(text, Tokenizer("english"))
    req_sentences = round(len(sent_tokenize(text)) * 0.70)
    summarizer = TextRankSummarizer()
    summary = summarizer(parser.document, req_sentences)

    ext_summary = " ".join(str(sentence) for sentence in summary)
    return ext_summary

def clean_summary(text):
    error_dict = [...]
    for error in error_dict:
        if error == text:
            return text

    irrelevant_terms = ["[music]", "[Music]", "\n", "<<", ">>"]
    sentence_list = [sentence.replace(item, "").strip() for sentence in sent_tokenize(text) for item in irrelevant_terms]
    cleaned_text = " ".join(sentence.capitalize() for sentence in sentence_list)
    normalized_text = unicodedata.normalize('NFKD', cleaned_text)
    formatted_text = normalized_text.encode('ascii', 'ignore').decode('ascii')
    return formatted_text.replace("\'", "'")

# Example usage
print(get_summary(True, "Hi, I'm Ollie, welcome to Oxford Online English. In this lesson, you can learn how to talk about your free time and your hobbies. Do you have any interesting hobbies? Talking about your free time is a good way to start a conversation in the English language or bring up things in common with the person you are talking to. At the end of this lesson, you will be able to talk clearly and naturally about your free time and hobbies in English. Part One: Words related to your hobbies and free time. What are the words?  What do you know in English?  Some people prefer what they can do at home, such as watching TV, reading or cooking.  Others prefer sports, such as playing football, basketball, tennis, swimming, going jogging, going climbing, or perhaps going boxing, doing judo, or practicing yoga. Of course, many people prefer more social activities, for example, going out with friends.  Or relax with family or go shopping.  Or maybe you prefer something more creative, such as photography, drawing, writing stories or writing a blog.  What about you?  What kind of free time activities do you prefer?  Let's look at how you can talk about your favorite free time activities and hobbies Part Two: What do you like to do?  -In my free time I love...  .  .  What can you say here? “In my free time, I like to play basketball.” “In my free time, I like to relax with my family.” “In my free time, I like to read books.”  Do you see a pattern here?  In every sentence, after “like” we use an additional verb -ing.  Can you put together a sentence?  What do you like to do in your free time?  But using only like would be repetitive and boring.  So what other verbs can be used? Well, you can use verbs like “I like,” “I enjoy,” or “I hate.”  For example: I like to go swimming. “I enjoy watching TV.” “I hate going shopping.”  Do you notice the same pattern?  After all of these verbs, you need to use a verb with -ing.  You can also add words like really and sometimes, or never, to make your meaning stronger or weaker.  For example: “I really like taking pictures.” “Sometimes I enjoy running.” “I absolutely hate playing soccer.” Now it’s your turn.  What can you say? Can you come up with your own sentences?  Well, now you can say something about what you like or don't like doing.  Let's look at how you can add more detail to your ideas.  First, let's say how often you do work in your free time. For example: I like to exercise. I play football every Tuesday evening.I absolutely hate going shopping. I only go shopping once or twice a year.” “I really like taking pictures, but I don’t get a chance to do it very often.” “What about you?  How often do you do your hobbies? You can use these phrases to help you speak.  all .  For example: “Every weekend,” “ Every Saturday afternoon,” “Every day.” Once or twice.  .  , for example: “Once a week”, “ Twice a month”, “Three times a year”, and so on. Can you make some sentences like this about your free time and hobbies? How often do you do your hobbies? Next, let's add some details about  Where do you do your hobby or leisure activity? For example: “I like to exercise.  I play football every Tuesday evening in the park near my house.” “ I enjoy drinking coffee with my friends.  We go to a café in the city center once or twice a week. “I really prefer photographing wildlife in the forest, but I don't get the opportunity to do that very often.” You can notice that our answers have become more detailed. When you speak you should always try to add some detail.  For your idea. That will make your English sound more natural and interesting. What about you? Can you add some details like this to your sentence? Pause the video. Practice. Try to come up with some sentences. Say them out loud. Practice a little. Okay. Next, let's have  Look at the background information, especially if you have an unusual interest or hobby. You can talk about when and why you started doing it. For example, “I started playing tennis when I was ten.” “ I was learning to draw for six months.” “I decided to take up yoga  Because I want to be healthy." "My French friend recommended me to climb.In the last sentence, the phrase My French friend recommended me to climb means that your friend came and offered you this thing (activity), and now you like it. What can you say about your hobbies? Can you use one of these phrases?  To speak for yourself? For example, I started climbing when I was living in Russia. I climbed for about eight years.  I also recently decided to do yoga because I want to be more flexible. When I was younger, my father took me into photography.  What about you?  What are your examples? Finally, let's take a look at how to add some descriptive words to say why you do or dont enjoy something.  For example, “I like climbing because its really exciting.”  I love doing yoga because its really relaxing.I really like writing stories because it is creativity, and I like using my imagination.”  You can also use negative adjectives to talk about things you don't like, for example, I don't like running because its tiring." "I hate watching TV because I find it boring." " I tried to learn to draw, but its very difficult. Why do you like your hobbies?  What activities do you not like to do? Can you say why you don't like them? Try to put together some sentences and practice this language.  Well it's your turn to speak. Lets try to use all of this to create a long answer.  For example: “I really like playing tennis. I play it every weekend in a park near my house. Sometimes I play it with my brother. Or sometimes with my friends. My brother recommended it to me because he loves sports. He needed someone to play with. I didn’t like it at first because it was difficult.”  I was wasting time. But now, I enjoy it, especially when I beat my brother. Well lets do another simple answer.  “I like taking pictures. Once or twice a month, I go to different areas of the city and look for interesting pictures. I have been interested in photography since I was young, when my father got me a camera for my birthday. I like it because it is creative work. I can express myself through  Through my photos. Everyone can use a camera, but you have to use your imagination to find the best photos to take. Now can you talk about your free time?  What do you like to do?  Where do you go and how often? When did you start practicing this hobby?  Why do you like or, preferably, hate this activity? Try to speak for at least 30 seconds.  Provide lots of details.  Add details to make your answer more interesting and important. This is the end of the lesson.  Thank you very much for watching.  I hope you learned something about talking about your free time in English.  You can watch more free lessons on our website: www.oxfordonlineenglish.com.", 1))

pip install googletrans

import os
from pytube import YouTube
import whisper
import warnings
from pytube.captions import Caption

warnings.filterwarnings("ignore", message="FP16 is not supported on CPU; using FP32 instead")

manual_subtitles = False

def eng_aliases():
    # Add aliases for English languages
    LANGUAGES['en-us'] = 'English'
    LANGUAGES['en-US'] = 'English'
    LANGUAGES['en-gb'] = 'English'
    LANGUAGES['en-GB'] = 'English'

def fetch_transcript_with_existing_subtitles(youtube_url):
    # Initialize a YouTube object
    yt = YouTube(youtube_url)
    title = yt.title
    print("Video Title:", title)
    eng_aliases()

    # Check if there are available captions (subtitles)
    available_captions = yt.captions.all()

    # Check if there are manually generated subtitles (e.g., "en" for English)
    manual_caption = None
    for caption in available_captions:
        if caption.code in ["en", "en-us", "en-gb"]:
            manual_caption = caption
            break

    if manual_caption:
        manual_caption.download(title)
        # Load and extract the captions
        with open(title + '.srt', 'r', encoding='utf-8') as file:
            subtitles = Caption.get_srt_captions(file.read())

        # Combine and format the subtitles into a transcript
        transcript = ' '.join([subtitle.text for subtitle in subtitles])
        return transcript
    else:
        return None  # No captions available

def fetch_transcript_with_ASR(youtube_url, has_audio_file=False):
    # Output file name
    output_file = "output.web3"

    # Create a temporary directory to store the video and audio files
    temp_dir = "temp"
    os.makedirs(temp_dir, exist_ok=True)
    yt = YouTube(youtube_url)
    title = yt.title
    print(title)
    name = title + ".mp4"
    file_location = "/content/" + temp_dir + "/" + name
    stream = yt.streams.filter(only_audio=True, file_extension="mp4").first()
    stream.download(output_path=temp_dir)
    model = whisper.load_model("base")
    result = model.transcribe(file_location)
    print(result["text"])

def main(youtube_url):
    # Check if the video has existing subtitles
    transcript = fetch_transcript_with_existing_subtitles(youtube_url)

    if transcript:
        print("Using Existing Subtitles:")
        print(transcript)
    else:
        print("No Existing Subtitles. Using ASR:")
        asr_transcript = fetch_transcript_with_ASR(youtube_url)
        print(asr_transcript)

if __name__ == "__main__":
    youtube_url = "https://www.youtube.com/watch?v=2qi7wEsd7_4"  # Change to your desired YouTube URL
    main(youtube_url)
