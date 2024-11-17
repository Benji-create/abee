# @title Generate Recipes - Account 2,3 & 4
!pip install gspread oauth2client openai youtube_transcript_api numpy requests beautifulsoup4 --quiet
!pip install git+https://github.com/pytube/pytube.git@refs/pull/2055/head --quiet
!pip install --upgrade openai --quiet
!pip install anthropic --quiet

from google.colab import auth
from google.auth import default
import json
from openai import OpenAI
import re
import requests
import base64
import gspread
from google.colab import auth
from oauth2client.client import GoogleCredentials
from pytube import YouTube, extract
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import JSONFormatter
import numpy as np
from bs4 import BeautifulSoup
import random
import time
import anthropic
import uuid
import concurrent.futures
from typing import List, Tuple
import time

# Authenticate and create the PyDrive client
auth.authenticate_user()
credentials = GoogleCredentials.get_application_default()


# Gemeinsame Konstanten und Client-Initialisierung
client = OpenAI(api_key="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")

def pintitles(title):
    """
    Writes multiple Pintitles
    """

    messages = [
    {
        "role": "system",
        "content": "Please give me 10 title suggestions for Pinterest Pins. The titles should be plain and short.\nThe titles must contain buzzwords like \"best\", \"healthy\", \"quick\", \"easy\", \"juicy\", \"tasty\" etc. \n\nThe buzzwords must fit well to the main keyword.\n\nExamples: \"Fluffy High Protein Cottage Cheese Pancakes\" \"Quick & Healthy Cottage Cheese Chicken Salad\"\n\nGive me suggestions with using the word \"recipe\" and without using it.\n\nAlso make suggestions using the given secondary keywords and without using them.\n\nAlways keep the keyword and do not change it."
    },
    {
        "role": "user",
        "content": "Main keyword: cottage cheese banana muffins \nSecondary keywords: high protein, healthy"
    },
    {
        "role": "assistant",
        "content": "Best Cottage Cheese Banana Muffins Recipe\nEasy Cottage Cheese Banana Muffins Recipe\nHealthy Cottage Cheese Banana Muffins\nQuick High Protein Cottage Cheese Banana Muffins\nMoist Cottage Cheese Banana Muffins\nTasty Cottage Cheese Banana Muffins Recipe\nFluffy Cottage Cheese Banana Muffins\n5-Minute Cottage Cheese Banana Muffins\nProtein-Packed Cottage Cheese Banana Muffins\nDelicious Healthy Cottage Cheese Banana Muffins"
    },
    {
        "role": "user",
        "content": "Main keyword: cottage cheese pancakes \nSecondary keywords: Easy, low calorie, high protein, healthy"
    },
    {
        "role": "assistant",
        "content": "Easy Cottage Cheese Pancakes Recipe\nHealthy Cottage Cheese Pancakes Recipe\nLow Calorie Cottage Cheese Pancakes\nFluffy Cottage Cheese Pancakes\nHigh Protein Cottage Cheese Pancakes\nQuick & Easy Cottage Cheese Pancakes\nBest Cottage Cheese Pancakes Recipe\nTasty Low Calorie Cottage Cheese Pancakes\nHealthy High Protein Cottage Cheese Pancakes\nDelicious Cottage Cheese Pancakes Recipe"
    },
    {
        "role": "user",
        "content": f"Main keyword: {title}"
    },
]

    response = client.chat.completions.create(
        messages=messages,
        #model="llama3-70b-8192",
        model="gpt-4o-mini",
        temperature=1,
        max_tokens=200,
        top_p=1,
        stop=None
    )
    return response.choices[0].message.content

def htmlliste(ingr):
# Entferne den einleitenden Satz und leere Zeilen, ignoriere Groß-/Kleinschreibung
    ingredients = [
        line.strip() for line in ingr.split('\n')
        if line.strip() and not line.lower().startswith('here is')
    ]
    html_output = '<h2>Ingredients</h2>\n<ul class="ingr">\n' + ''.join(f'    <li>{ingredient.capitalize()}</li>\n' for ingredient in ingredients) + '</ul>\n<div class="hr--handdrawn"></div>'

    return html_output

def htmlsteps(steps):
    """
    Writes HTML Steps with h2.
    """

    messages = [
    {
        "role": "system",
        "content": "You are a pro at writing recipes. \nYou use basic US English. \nThe focus is always on reader-friendliness and usability. \nYour task is to structure the recipe well and group the single steps into 3-6 work steps that are absolutely sensible for the user. \nDo not give me a list of ingredients. Only reply with the steps.\nPlease output the text in HTML format.\nAlways begin the headline with \"Step 1:\", \"Step 2:\"..."
    },
    {
        "role": "user",
        "content": "Please write a recipe for my blog article for the topic \"Cottage Cheese Alfredo Sauce | High Protein & Creamy\". \n\nPlease use the following steps to create the recipe:\n\n1. Add 1 and 1/2 cups of cottage cheese, half a cup of milk, 1 and 1/2 teaspoons of Italian seasoning, half a cup of grated Parmesan cheese, half a teaspoon of black pepper, and a pinch of salt to a blender or food processor.\n2. Blend everything together until smooth.\n3. If the mixture is too thick, add a little more milk or some higher protein bone broth.\n4. Take out a stove top pan and turn the burner on low heat, then add in 1 and 1/2 tablespoons of butter.\n5. Once the butter melts, add in a tablespoon of minced garlic and let it cook for a few minutes.\n6. Pour in the cottage cheese mixture and a teaspoon of corn starch, and keep stirring often as everything heats up and begins to thicken.\n7. Cook on low heat, as high heat can ruin the sauce.\n8. While the sauce is heating up, cook some pasta according to the package instructions.\n9. Once the pasta is done, drain it and add it to the Alfredo sauce.\n10. Mix everything around for a couple of minutes, then add in any additional ingredients you like (such as cooked protein or crushed red pepper).\n11. Serve hot, and reheat as needed by mixing in a little milk and reheating over low heat.\n\nPlease output a text divided into several steps that are marked as h2 header. \nGroup the single steps into meaningful headlines. \nDo not give me a list of ingredients. Only reply with the steps.\nPlease output the text in html format."
    },
    {
        "role": "assistant",
        "content": "<h2>Step 1: Blend the Cottage Cheese Mixture</h2>\n<p>Start by adding 1 and 1/2 cups of cottage cheese, half a cup of milk, 1 and 1/2 teaspoons of Italian seasoning, half a cup of grated Parmesan cheese, half a teaspoon of black pepper, and a pinch of salt into a blender or food processor. Blend until the mixture becomes smooth and creamy. If the mixture seems too thick, you can adjust the consistency by adding a bit more milk or some higher protein bone broth.</p>\n\n<h2>Step 2: Prepare the Garlic Butter</h2>\n<p>Place a stovetop pan over low heat and melt 1 and 1/2 tablespoons of butter in it. Once the butter is melted, add a tablespoon of minced garlic and let it cook for a few minutes until fragrant. Be careful not to burn the garlic.</p>\n\n<h2>Step 3: Combine and Heat the Sauce</h2>\n<p>Pour the blended cottage cheese mixture into the pan with the garlic butter. Add a teaspoon of corn starch, then stir continuously as the sauce begins to heat and thicken. Maintain the heat at a low setting to prevent the sauce from curdling or separating.</p>\n\n<h2>Step 4: Cook the Pasta</h2>\n<p>As the sauce is warming up, cook your favorite pasta according to the package instructions. Once the pasta is al dente, drain it well and immediately add it to the pan with the Alfredo sauce. Stir everything together to ensure the pasta is evenly coated with the creamy sauce.</p>\n\n<h2>Step 5: Final Touches and Serve</h2>\n<p>If you want to add extra flavor or protein, incorporate any additional ingredients like cooked chicken, shrimp, or a sprinkle of crushed red pepper at this stage. Mix everything thoroughly and serve hot. If the sauce thickens too much upon reheating, simply add a splash of milk and reheat over low heat until smooth again.</p>"
    },
    {
        "role": "user",
        "content": "1. Get a large measuring cup or a medium-sized bowl and place it on a food scale.\n2. Measure out 42 grams (less than 1/3 cup) of almond flour into the bowl.\n3. Add 1/4 teaspoon of baking powder to the bowl.\n4. Add 1/4 teaspoon of xanthan gum (or guar gum as a substitute) to the bowl.\n5. Add a pinch of salt to the bowl.\n6. Add some garlic powder and onion powder to the bowl for flavor.\n7. Add 2 tablespoons (22 grams) of water to the bowl and mix until a thick, sticky dough forms.\n8. Coat an 8-ounce ramekin with baking spray.\n9. Add the dough to the ramekin and spread it out evenly using a spatula coated with water.\n10. Microwave the pizza dough for 1 minute or bake in the oven at 350\u00b0F (175\u00b0C) for 20 minutes.\n11. Remove the pizza crust from the microwave or oven and add 2 tablespoons (30 grams) of pizza sauce.\n12. Add less than a quarter cup (21 grams) of full-fat mozzarella cheese on top of the pizza sauce.\n13. Add mini slices of pepperoni on top of the cheese.\n14. Microwave the pizza for 30 seconds on the left side, then 30 seconds on the right side, or broil in the oven for a few minutes until the cheese melts."
    },
    {
        "role": "assistant",
        "content": "<h2>Step 1: Measure and Combine Dry Ingredients</h2>\n<p>Begin by getting a large measuring cup or a medium-sized bowl and placing it on a food scale. Measure out 42 grams (less than 1/3 cup) of almond flour into the bowl. Add 1/4 teaspoon of baking powder, 1/4 teaspoon of xanthan gum (or guar gum as a substitute), a pinch of salt, and some garlic powder and onion powder for flavor. Mix these dry ingredients together thoroughly.</p>\n\n<h2>Step 2: Add Water and Form the Dough</h2>\n<p>To the bowl of combined dry ingredients, add 2 tablespoons (22 grams) of water. Mix until a thick, sticky dough forms. This may take a little bit of effort to ensure all the dry ingredients are fully integrated into the water.</p>\n\n<h2>Step 3: Prepare the Ramekin and Spread the Dough</h2>\n<p>Coat an 8-ounce ramekin with baking spray to prevent the dough from sticking. Add the dough to the ramekin and spread it out evenly using a spatula coated with water to keep the dough from sticking to the spatula.</p>\n\n<h2>Step 4: Cook the Pizza Crust</h2>\n<p>Microwave the pizza dough for 1 minute, or alternatively, bake in the oven at 350\u00b0F (175\u00b0C) for 20 minutes until the crust is set and slightly golden. This will create a solid base for the toppings.</p>\n\n<h2>Step 5: Add Toppings and Melt the Cheese</h2>\n<p>Remove the pizza crust from the microwave or oven. Spread 2 tablespoons (30 grams) of pizza sauce over the crust. Sprinkle less than a quarter cup (21 grams) of full-fat mozzarella cheese on top of the sauce. Add mini slices of pepperoni over the cheese. Microwave the pizza for 30 seconds on the left side, then 30 seconds on the right side, or broil in the oven for a few minutes until the cheese melts and becomes bubbly.</p>\n\n<h2>Step 6: Serve and Enjoy</h2>\n<p>Once the cheese has melted to your liking, remove the ramekin from the microwave or oven, being careful as it will be hot. Let the pizza cool for a minute before digging in. Enjoy your quick and delicious personal pizza!</p>"
    },
    {
        "role": "user",
        "content": steps
    }
]

    response = client.chat.completions.create(
        messages=messages,
        #model="llama3-70b-8192",
        model="gpt-4o",
        temperature=1,
        max_tokens=1024,
        top_p=1,
        stop=None
    )

    content = response.choices[0].message.content

   # Nachbearbeitung des Inhalts
    paragraphs = content.split('\n')
    formatted_paragraphs = []

    for i, paragraph in enumerate(paragraphs):
        if paragraph.strip():
            if re.match(r'<h[1-6]>', paragraph):
                # Füge einen Trenner vor jeder <h2>, außer vor der ersten
                if i > 0 and re.match(r'<h2>', paragraph):
                    formatted_paragraphs.append('<div class="hr--handdrawn"></div>')
                formatted_paragraphs.append(paragraph.strip())
            else:
                # Entfernen Sie zusätzliche Punkte am Ende der Sätze
                paragraph = re.sub(r'\.+', '.', paragraph)
                # Teilen Sie den Absatz in Sätze
                sentences = re.split(r'(?<=[.!?])\s+', paragraph.strip())
                # Fügen Sie jeden Satz als separaten Absatz hinzu
                formatted_paragraphs.extend(sentences)

    formatted_content = '\n\n'.join(formatted_paragraphs)

    return formatted_content

def introgen(content):
    
    client = anthropic.Anthropic(api_key="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")


    INTRO_EXAMPLES = """
<example 1> What's better than a Strawberry Pop-Tart? A huge strawberry pop tart slab pie! 

This strawberry pop tart slab pie is an amped-up version of your favorite Pop-Tart from the store. Serve it as a dessert, for an indulgent breakfast or weekend brunch, or pack little squares in lunch boxes. If you think a giant pop tart would last long, think again. </example 1>

<example 2> I was an adult before I knew it was possible to successfully cook bacon any other way than in the microwave. It's how my mom always did it. When dad did it on the stove, it burned to a crisp.

That's because dad's bacon cooking technique was off—he was using high heat, and bacon in a skillet likes it low and slow. Microwave bacon, on the other hand, requires no technique outside of pressing buttons. For the cooking-impaired, it's foolproof. </example 2>

<example 3> Figuring out a go-to, healthy breakfast for hectic weekday mornings can be a major challenge. After all, healthy breakfasts are rarely attainable when you're up against the clock to catch your train on time, or beat the inevitable traffic jams on your daily commute, and things get even more challenging when kids are involved.

Luckily, these kale and mushroom egg bites check all the boxes: they're healthy yet delicious, simple to meal prep and reheat, and endlessly adaptable to whatever ingredients you have on hand. </example 3>
"""


    # Split the string into examples
    examples = INTRO_EXAMPLES.split('<example')[1:]
    
    # Randomly select an example and get its index
    selected_index = random.randint(0, len(examples) - 1)
    selected_example = examples[selected_index].split('</example')[0].strip()
    
    # Print which example was chosen
    print(f"Using example {selected_index + 1}")

    PROMPT=f"""
You are tasked with writing an introductory paragraph for a recipe blog article. The recipe you'll be introducing is:

<recipe_name>
{content}
</recipe_name>

When writing the intro, follow these guidelines:

1. Use a casual, conversational tone as if you're talking to a friend.
2. Write at a 10th-grade English level - keep it simple and easy to understand.


Avoid the following:
- Do not use these words: ultimate, stunning, vibrant, enhance, transform, admired, versatile, delicate, breathtaking, captivating
- Refrain from using strong adjectives.

Your intro should mimic the style, tone, and sentence structure of this Example:

<example>
{selected_example}
</example>

ONLY REPLY WITH THE INTRO NOTHING ELSE!!
"""
    
    try:
        message = client.messages.create( 
            #client.chat.completions.create(
            model="claude-3-5-sonnet-latest",
            model="gpt-4o",
            max_tokens=500,
            temperature=1,
            messages=[
                # {
                #     "role": "system",
                #     "content": [
                #         {
                #         "type": "text",
                #         "text": "Vary your paragraph openings. Do not start your paragraph with the same topic as any previous responses!\n\nEnsure diversity in your responses. Avoid using the same themes or topics in consecutive paragraphs. Always aim for variety in both content and structure. Rotate through different aspects of the tree and its characteristics to keep the information fresh and engaging. \n\nBe mindful of your previous responses and consciously choose different starting points and focus areas for each new paragraph"
                #         }
                #     ]
                # },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": PROMPT
                        }
                    ]
                }
            ]
        )
        return message.content[0].text
        #return message.choices[0].message.content
    
    except Exception as e:
        return f"API-Fehler: {str(e)}"

def table(title, steps):
    """
    Creates JSON Prep Time and Converts into HTML Table.
    """


    messages = [
    {
        "role": "system",
        "content": "Please output in JSON format the following values:\n\nPreparation Time\nCooking Time\nTotal Time\nLevel of Difficulty\n\nFor the Level of Difficulty you have the range of Easy, Medium and Hard. \n\nAlways specify the output in minutes and in range minimum to maximum."
    },
    {
        "role": "user",
        "content": "Recipe Name: Cottage Cheese Alfredo Sauce Creamy & High Protein\n\nCalculate the values from the system prompt based on the following steps:\n\n1. Gather ingredients: 2 eggs and 1 cup of cottage cheese.\n2. Add flavorings (optional): up to 1 teaspoon of herbs or spices, such as garlic spread and chives.\n3. Blend eggs, cottage cheese, and flavorings in a blender or Thermomix until well combined.\n4. Prepare a 9x13 pan by lining it with parchment paper.\n5. Pour the dough onto the parchment paper and spread it out into a rectangle shape.\n6. Bake in a preheated oven at 375°F (190°C) for 2 hours, or at 350°F (175°C) for 2.5 hours.\n7. Remove from the oven and let cool.\n8. Use the flatbread to make sandwiches, wraps, or as a pizza crust.\n9. Store leftovers wrapped tightly in plastic or foil in the fridge, or freeze for later use.\n\nAnswer with JSON Output.\n"
    },
    {
        "role": "assistant",
        "content": "{\n\"Preparation Time\": \"15-30 minutes\",\n\"Cooking Time\": \"120-150 minutes\",\n\"Total Time\": \"135-180 minutes\",\n\"Level of Difficulty\": \"Easy\"\n}"
    },
    {
        "role": "user",
        "content": str(f"Recipe Name: {title}\n\nSteps:\n{steps}")
    }
    ]


    response = client.chat.completions.create(
        messages=messages,
        #model="llama3-70b-8192",
        model="gpt-4o-mini",
        temperature=1,
        max_tokens=200,
        top_p=1,
        response_format={"type": "json_object"}
        #stop=None
    )

    jdata = response.choices[0].message.content

    # JSON-Daten in ein Python-Wörterbuch umwandeln
    data = json.loads(jdata)

    # HTML-Tabellenanfang
    html_table = "<table>\n<tbody>\n"

    # Tabellenkopf und Datenzeilen hinzufügen
    html_table += "".join(f"<tr><td><b>{key}</b></td><td>{value}</td></tr>\n" for key, value in data.items())

    # HTML-Tabellenende
    html_table += '</tbody>\n</table>\n<div class="hr--handdrawn"></div>'

    # Ergebnis ausgeben
    return html_table

     #+ '\n<div class="hr--handdrawn"></div>'

def upload_to_wordpress(article_html, wp_base_url, wp_username, wp_password, title):
    credentials = f"{wp_username}:{wp_password}"
    token = base64.b64encode(credentials.encode())
    headers = {
        'Authorization': f'Basic {token.decode("utf-8")}',
        'Content-Type': 'application/json'
    }

    data = {
        'title': title,
        'content': article_html,
        'status': 'publish',
        #'status': 'draft',
        'categories': [3]
    }

    response = requests.post(f'{wp_base_url}/wp-json/wp/v2/posts', headers=headers, json=data)

    if response.status_code == 201:
        post_data = response.json()
        draft_url = post_data['link']
        print(f"WordPress URL: {draft_url}")
        return draft_url
    else:
        print(f"Fehler beim Hochladen des Artikels nach WordPress: {response.content}")
        return None

def build_metadata(url: str) -> dict:
    """
    Build metadata for a given YouTube URL.
    Args:
        url (str): The URL of the YouTube video.
    Returns:
        dict: A dictionary containing video metadata such as title, length, views, and description.
    """
    yt = YouTube(url)
    #print(yt.thumbnail_url)
    return {
        "title": yt.title,
        #"length": yt.length,
        #"views": yt.views,
        "description": get_description(yt)
    }

def get_description(yt):
    """
    Retrieve the description of a YouTube video.
    Args:
        yt (YouTube): The YouTube object.
    Returns:
        str: The description of the YouTube video.
    """
    for n in range(6):
        try:
            description = yt.initial_data["engagementPanels"][n][
                "engagementPanelSectionListRenderer"]["content"][
                    "structuredDescriptionContentRenderer"]["items"][1][
                        "expandableVideoDescriptionBodyRenderer"][
                            "attributedDescriptionBodyText"]["content"]
            return description
        except:
            continue
    return ""

def get_youtube_transcript(url: str) -> dict:
    """
    Retrieve the transcript for a given YouTube video URL.
    Args:
        url (str): The URL of the YouTube video.
    Returns:
        dict: The transcript of the YouTube video in dictionary format. If the URL is invalid, return an empty dictionary.
    """
    yt_api = YouTubeTranscriptApi()
    formatter = JSONFormatter()
    video_id = extract.video_id(url)
    transcript = yt_api.get_transcript(video_id, languages=['en', 'en-US'])
    return formatter.format_transcript(transcript)

def extract_ingredients(transcript: str, metadata: dict) -> str:
    """
    Extract ingredients list from the YouTube transcript and video metadata using a chat model.
    Args:
        transcript (str): The transcript of the YouTube video.
        metadata (dict): The metadata of the YouTube video.
    Returns:
        str: Extracted ingredients list.
    """

    INGREDIENT_PROMPT = """
    You are a helpful assistant that extracts ingredients from recipe videos.
    Your goal is to provide a clear and concise list of ingredients based on the given transcript and video metadata.
    Return ONLY the list of ingredients, one per line, with quantities if available.
    If no ingredients are found in the Transcript, try to extracts ingredients from the video description.
    Do not include any other text or explanations.
    For example:
    2 cups all-purpose flour
    1 cup sugar
    3 eggs
    1/2 cup milk
    """

    messages = [
        {"role": "system", "content": INGREDIENT_PROMPT},
        {"role": "user", "content": f"Video metadata: {json.dumps(metadata)}"},
        {"role": "user", "content": transcript}
    ]

    response = client.chat.completions.create(
        messages=messages,
        #model="llama3-70b-8192",
        model="gpt-4o-mini",
        temperature=0.5,
        max_tokens=1024,
        top_p=0.25,
        stop=None
    )
    return response.choices[0].message.content

def summarize_yt(url):
    """
    Summarize a YouTube transcript using a chat model and extract ingredients.
    Args:
        url (str): The URL of the YouTube video.
    Returns:
        str: Summarized content of the YouTube video and extracted ingredients.
    """
    transcript = get_youtube_transcript(url)
    #print(transcript)
    metadata = build_metadata(url)
    #print(metadata)


    SYSTEM_PROMPT = """
    You are a helpful assistant that creates step-by-step instructions based on segments of a video.
    Your goal is to provide a clear and detailed recipe instruction from the given content.
    Return ONLY the instructions and NO OTHER TEXT.
    Do not refer to the "video" or "youtube" in your response. Instead, organize instructions as numbered steps.
    For example:
    1. Preheat the oven to 350°F (175°C).
    2. Mix flour and sugar in a bowl.
    """

    messages = [
    {
        "role": "system",
        "content": SYSTEM_PROMPT
    },
    {
        "role": "system",
        "content": f"video metadata: {metadata}",
    }
    ]

    CHUNKS = 1

    chunked_transcript = list(np.array_split(json.loads(transcript), CHUNKS))

    title = f"{metadata['title']}"
    #print(title)
    # Extract ingredients using full metadata
    ingredients = extract_ingredients(' '.join([s['text'] for s in json.loads(transcript)]), metadata)
    #print(ingredients)
    ingr = f"{ingredients}"

    start = 0
    for chunk in chunked_transcript:
        end = max([round(s['start'] + s['duration'], 0) for s in chunk])
        text = [s['text'] for s in chunk]
        transcript = f"""
        start_seconds: {start}
        end_seconds: {end}
        transcript: {' '.join(text)}
        """


        messages.append({"role": "system", "content": transcript})
        response = client.chat.completions.create(messages=messages,
                                                  #model="llama3-70b-8192",
                                                    model="gpt-4o-mini",
                                                  temperature=1,
                                                  max_tokens=1024,
                                                  top_p=0.25,
                                                  stop=None)
        response_content = str(response.choices[0].message.content)
        messages.append({"role": "assistant", "content": response_content})
        #{int(start)} - {int(end)}

        ins = f"{response_content}"
        start = end

    #print(title, ingr, ins)

    return title, ingr, ins

def genrecipe(url):

    def jinaextract(url):
          STEPS_PROMPT = """
          You are a helpful assistant that creates step-by-step instructions based on a Textinput.
          Your goal is to provide a clear and detailed recipe instruction from the given content.
          Return ONLY the instructions in neutral tone of voice and NO OTHER TEXT.
          Do not refer to "Recipe" or "youtube" in your response. Instead, organize instructions as numbered steps.

          For example:
          1. Preheat the oven to 350°F (175°C).
          2. Mix flour and sugar in a bowl.
          """

          INS_PROMPT ="""
          You are a helpful assistant that extracts ingredients from text.
          Your goal is to provide a clear and concise list of ingredients based on the given text.
          Return ONLY the list of ingredients, one per line, with quantities if available.
          Do not include any other text or explanations.

          For example:
          2 cups all-purpose flour
          1 cup sugar
          3 eggs
          1/2 cup milk
          """


          response = requests.get(f'https://r.jina.ai/{url}')

          print(url)

          # Dein Markdown-Text
          markdown_text = response.text

          # Entferne Links (Markdown-Syntax für Links: [Text](URL))
          markdown_text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', markdown_text)

          # Entferne Bilder (Markdown-Syntax für Bilder: ![Alt-Text](URL))
          markdown_text = re.sub(r'!\[([^\]]*)\]\([^\)]+\)', '', markdown_text)

          rawingr = client.chat.completions.create(
          model="gpt-4o-mini",
          messages=[
              {
                  "role": "system",
                  "content": INS_PROMPT
              },
              {
                  "role": "user",
                  "content": markdown_text
              }
          ],
          temperature=0,
          max_tokens=250,
          top_p=1,
          stream=False,
          stop=None,
          )

          steps = client.chat.completions.create(
          model="gpt-4o-mini",
          messages=[
              {
                  "role": "system",
                  "content": STEPS_PROMPT
              },
              {
                  "role": "user",
                  "content": markdown_text
              }
          ],
          temperature=0,
          max_tokens=250,
          top_p=1,
          stream=False,
          stop=None,
      )


          return rawingr.choices[0].message.content, steps.choices[0].message.content

    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Safari/605.1.15',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0'
    ]

    headers = {
        'User-Agent': random.choice(user_agents),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Referer': 'https://www.google.com/',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }




    try:
        session = requests.Session()
        response = requests.session().get(url, headers=headers, timeout=10, verify=False)
        response.raise_for_status()  # This will raise an exception for 4xx and 5xx status codes
    except (requests.exceptions.RequestException, requests.exceptions.HTTPError):
        print('Request blocked or failed, using jina.ai....')
        ingredients, steps = jinaextract(url)
    else:

      soup = BeautifulSoup(response.text, 'html.parser')

      ingredients = None
      steps = None

      # Finde alle <script> Tags mit type 'application/ld+json'
      schema_scripts = soup.find_all('script', type='application/ld+json')

      for script in schema_scripts:
          try:
              # Möglicherweise enthält das Skript mehrere JSON-Objekte
              data = json.loads(script.string)
          except json.JSONDecodeError:
              # Manchmal sind mehrere JSON-Objekte ohne Kommas getrennt
              try:
                  data = [json.loads(item) for item in script.string.strip().split('\n') if item.strip()]
              except json.JSONDecodeError:
                  continue  # Wenn dennoch nicht parsebar, weitermachen

          #Definiere eine rekursive Funktion zur Suche nach dem Recipe-Objekt
          def find_recipe(obj):
            if isinstance(obj, dict):
                obj_type = obj.get('@type', '')
                if isinstance(obj_type, list):
                    obj_type = [t.lower() if isinstance(t, str) else t for t in obj_type]
                elif isinstance(obj_type, str):
                    obj_type = obj_type.lower()
                else:
                    obj_type = ''

                if 'recipe' == obj_type or (isinstance(obj_type, list) and 'recipe' in obj_type):
                    return obj
                for value in obj.values():
                    result = find_recipe(value)
                    if result:
                        return result
            elif isinstance(obj, list):
                for item in obj:
                    result = find_recipe(item)
                    if result:
                        return result
            return None

          recipe = find_recipe(data)

          if recipe:
              print('Use Schema Recipe Data...')
              # Extrahiere die Zutaten
              ingredients = recipe.get('recipeIngredient', [])
              if isinstance(ingredients, list):
                  ingredients = '\n'.join(ingredients)
              elif isinstance(ingredients, str):
                  ingredients = ingredients  # Falls es als String vorliegt

              # Extrahiere die Schritte
              instructions = recipe.get('recipeInstructions', [])
              def extract_steps(instructions_list):
                  steps_collected = []
                  if isinstance(instructions_list, list):
                      for instruction in instructions_list:
                          if isinstance(instruction, dict):
                              step_type = instruction.get('@type', '').lower()
                              if 'howtostep' == step_type:
                                  text = instruction.get('text', '').strip()
                                  if text:
                                      steps_collected.append(text)
                              elif 'howtosection' == step_type:
                                  # Rekursiver Aufruf für verschachtelte Schritte
                                  section_steps = extract_steps(instruction.get('itemListElement', []))
                                  steps_collected.extend(section_steps)
                          elif isinstance(instruction, str):
                              text = instruction.strip()
                              if text:
                                  steps_collected.append(text)
                  elif isinstance(instructions_list, dict):
                      # Falls es nur ein einzelnes Dict ist
                      steps_collected.extend(extract_steps([instructions_list]))
                  elif isinstance(instructions_list, str):
                      steps_collected.append(instructions_list.strip())
                  return steps_collected

              steps = extract_steps(instructions)
              steps = '\n'.join(steps)

              #print(steps)

              break #Beende die Schleife, wenn ein Rezept gefunden wurde


      session.close()





      # Wenn kein Schema gefunden wurde oder Informationen fehlen, verwende jinaextract
      if not ingredients or not steps:
          print('Can not find ingredients or steps, using jina.ai....')
          ingredients, steps = jinaextract(url)

    # Verarbeite die Zutaten mit der AI-Formel, unabhängig von der Quelle

    ingr = client.chat.completions.create(
        model="gpt-4o",

        messages=[
        {
        "role": "system",
        "content": """
        I give you a list with ingredients.
        Please adjust and rewrite the ingredient list to be less recognizable from its original version, without changing the recipe.
        Ensure that the quantities, measures, and forms remain clear but use different wording.
        Only give me maximum 2 measure units per ingredients.
        Only use frequently used words for synonyms no complicated words i.e. leavening agent
        Respond ONLY with the modified ingredient list, nothing else!
        """
    },
        {
            "role": "user",
            "content": "\n1 cup 4% milkfat cottage cheese\n\u00bc cup pure maple syrup\n1 teaspoon vanilla\n1 cup (106 grams) lightly packed almond flour\n2 Tablespoons melted coconut oil\n\u00bd cup (53 grams) vanilla protein powder\n\u00bd cup chocolate chips"
        },
        {
            "role": "assistant",
            "content": "1 cup creamy cottage cheese (4% milk fat)\n\u00bc cup authentic maple syrup\n1 teaspoon vanilla essence\n1 cup finely ground almond flour (approx. 106 grams)\n2 tablespoons coconut oil, melted\n50 grams vanilla-flavored protein powder (around \u00bd cup)\n\u00bd cup chocolate chips"
        },
        {
            "role": "user",
            "content": "1 cup / 8 oz / 227g plain cottage cheese (low-fat is fine)\n3/4 cup / 1 oz / 28g parmesan cheese, freshly grated\n1/4 cup / 1.25 oz / 35g flour (see headnotes)\n1 cup / 3.5 oz / 95g almond meal or almond flour, finely ground\n1 teaspoon baking powder\n1/4 cup / 60 ml water\n4 eggs, lightly beaten\n1/2 teaspoon salt\n1/3 cup fresh herbs (I like: 1 tablespoon fresh thyme, 1 tablespoon chopped, fresh oregano & 1/4 cup chopped chives)"
        },
        {
            "role": "assistant",
            "content": "1 cup plain cottage cheese (227g, low-fat is acceptable)\n3/4 cup freshly grated parmesan cheese (28g)\n1/4 cup any variety of flour (35g)\n1 cup finely ground almond meal or almond flour (95g)\n1 teaspoon baking powder\n1/4 cup water (60 ml)\n4 eggs, slightly beaten\n1/2 teaspoon salt\n1/3 cup chopped fresh herbs (such as 1 tablespoon thyme, 1 tablespoon oregano, and 1/4 cup chives)"
        },
        {
            "role": "user",
            "content": "1 cup cottage cheese\n2 large eggs\n\u00be cups quick cooking oats (use GF oats if needed)\n\u00bd teaspoon baking powder\n1 tablespoon cold-pressed virgin coconut oil"
        },
        {
            "role": "assistant",
            "content": "1 cup plain cottage cheese\n2 large eggs\n3/4 cup quick-cooking oats (use gluten-free if necessary)\n1/2 teaspoon baking powder\n1 tablespoon virgin cold-pressed coconut oil"
        },
        {
            "role": "user",
            "content": "2 1\u20443 cup cottage cheese (1% small curd)\n1 cup Greek yogurt (plain, nonfat)\n2 eggs (large organic)\n1\u20444 cup maple syrup (sugar free, pure, or your preferred liquid sweetener)\n1\u20448 cup monk fruit (or swerve or sugar substitute of choice)\n1\u20442 tsp vanilla extract\n1\u20448 tsp salt"
        },
        {
            "role": "assistant",
            "content": "2 1/3 cups small curd cottage cheese (1% fat)\n1 cup plain nonfat Greek yogurt\n2 large organic eggs\n1/4 cup pure maple syrup (or your choice of liquid sweetener)\n1/8 cup monk fruit sweetener (or preferred sugar substitute)\n1/2 teaspoon vanilla essence\n1/8 teaspoon salt"
        },
        {
            "role": "user",
            "content": str(ingredients)
        }
        ],

        temperature=1,
        max_tokens=250,
        top_p=1,
        stream=False,
        stop=None,
    )
    #print(ingr.choices[0].message.content)
    return ingr.choices[0].message.content, steps

# Function to generate serving suggestions
def generate_serving_suggestions(title, ingredients):


    client = anthropic.Anthropic(api_key="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")

    message = client.messages.create(
        model="claude-3-5-sonnet-20240620",
        max_tokens=600,
        temperature=0.9,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "You are tasked with writing a section about potential substitutions for ingredients in a recipe. Your goal is to provide helpful, practical alternatives while maintaining the dish's overall flavor profile and nutritional balance.\n\nThe recipe you will be analyzing is:\n<recipe_name>\n{Delicious Cottage Cheese Pumpkin Cheesecake}\n</recipe_name>\n\nHere are the ingredients for this recipe:\n<ingredients_list>\n{Ingredients\n1 carton cottage cheese\n1 1/2 cups graham crackers\n1/2 cup butter\n1 cup pumpkin puree\n1/2 cup maple syrup\n1/4 cup flour\n1 teaspoon pumpkin pie spice\n3 eggs\nBrown sugar (for meringue)\n}\n</ingredients_list>\n\nCarefully review each ingredient in the list. For 3 main items, consider possible substitutions that could work well in the recipe. \n\nFocus on alternatives that:\n1. Have similar flavor profiles or culinary functions\n2. Maintain or improve the nutritional value of the dish\n3. Accommodate common dietary restrictions or preferences (e.g., vegetarian, vegan, gluten-free, low-carb)\n4. Are reasonably accessible to most home cooks\n\nWhen suggesting substitutions, provide:\n1. At least one alternative for the top 3 main ingredients\n2. A brief explanation of why the substitution works\n3. Any necessary adjustments to cooking methods or quantities\n\nWrite your response in clear, straightforward language suitable for a 10th-grade reading level. Aim for high information density, avoiding unnecessary words or repetition. Do not use overly strong descriptive adjectives. Don't make bullet points. Write a paragraph with whole sentences.\n\nPresent your substitutions in a logical order, grouping related items together when appropriate. Use short, concise sentences.\n\nWrite your complete response inside <substitutions> tags."
                    }
                ]
            },
            {
                "role": "assistant",
                "content": [
                    {
                        "type": "text",
                        "text": "<substitutions>\nCottage cheese can be replaced with silken tofu for a vegan option, maintaining a creamy texture and boosting protein content. Use a 1:1 ratio and blend the tofu until smooth. \n\nGraham crackers can be swapped with gluten-free oats or almond flour for a gluten-free crust. Adjust the butter quantity as needed to achieve the right consistency. \n\nMaple syrup can be substituted with honey or agave nectar for different sweetness profiles. Use slightly less honey or agave, as they are sweeter than maple syrup. </substitutions>"
                    }
                ]
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"Recipe Name: {title}\n\nIngredients:\n{ingredients}\n"
                    }
                ]
            }
        ]
    )

    suggestions = message.content[0].text
    suggestions = suggestions.split('<substitutions>')[1].split('</substitutions>')[0].strip()

    # Define three different h2 options
    h2_options = [
        "<h2>Ingredient Substitutions</h2>\n",
        "<h2>Possible Ingredient Alternatives</h2>\n",
        "<h2>Suggestions for Ingredient Substitution</h2>\n"
    ]

    # Randomly choose one of the h2 options
    html_suggestions = random.choice(h2_options)
    html_suggestions += f"{suggestions}\n"
    html_suggestions += "<div class=\"hr--handdrawn\"></div>"

    return html_suggestions

# Nutrition Estimate
def nutritionestimate(ingredients):
    """
    Creates JSON Nutrition and Converts into HTML Table.
    """

    messages = [
    {
      "role": "user",
      "content": [
        {
          "type": "text",
          "text": "You are a nutrition expert tasked with estimating the nutritional content of a recipe based on its ingredient list. You will be provided with a list of ingredients and their amounts. Your goal is to estimate the nutritional values for the entire recipe and present them in a specific format.\n\nHere is the ingredient list for the recipe:\n<ingredient_list>\n{{INGREDIENT_LIST}}\n</ingredient_list>\n\nFollow these steps to complete the task:\n\n1. Carefully review the ingredient list, noting the ingredients and their quantities.\n\n2. Estimate the nutritional values for the entire recipe, focusing on these characteristics:\n   - Calories\n   - Protein\n   - Fat\n   - Carbohydrates\n\n3. For each nutritional characteristic, provide a range rather than a single value to account for estimation uncertainty. For example, \"Calories: 300-350\" instead of \"Calories: 325\".\n\n4. If there are any optional ingredients mentioned in the list, do not include them in your calculations. \n\n5. Present your estimated nutritional information in JSON format . Use the following structure:\n\n{\n  \"Calories\": \"X-Y\",\n  \"Protein\": \"A-B g\",\n  \"Fat\": \"C-D g\",\n  \"Carbohydrates\": \"E-F g\"\n}\n\n6. If there are no optional ingredients, omit the \"Note\" field from the JSON output. Only answer with the JSON output.\n\n7. If no quantities are specified, do not include them in the calculation, either.\n\nRemember, these are estimates based on the ingredient list provided. Actual nutritional values may vary depending on specific brands, preparation methods, and serving sizes."
        }
      ]
    },
    {
      "role": "assistant",
      "content": [
        {
          "type": "text",
          "text": "{\n  \"Calories\": \"350-400\",\n  \"Protein\": \"30-35 g\",\n  \"Fat\": \"22-26 g\",\n  \"Carbohydrates\": \"5-8 g\"\n}"
        }
      ]
    },
    {
      "role": "user",
      "content": [
        {
          "type": "text",
          "text": "4 large whole eggs\n1/2 cup cottage cheese\nSalt\nBlack pepper\nOil or butter (for cooking)\nOptional seasonings (e.g., garlic powder)\nChopped vegetables (optional)\nGround beef or turkey (optional)\nBacon bits (optional)\nChopped chives (optional)"
        }
      ]
    },
    {
      "role": "assistant",
      "content": [
        {
          "type": "text",
          "text": "8 ounces penne pasta\n1/2 teaspoon sea salt (for boiling water)\n2 skinless, boneless chicken breasts (around 1 pound)\nPinch each of salt and pepper (for chicken seasoning)\n1 tablespoon olive oil (or your choice of cooking oil)\n1 medium onion (chopped)\n3 cloves garlic (chopped)\n1/4 cup vodka\n1 can (28 ounces) crushed tomatoes\n1/2 cup heavy cream\n1/4 cup fresh oregano (or 1 teaspoon dried)\n1/4 teaspoon red pepper flakes\n1/4 cup grated parmesan cheese (plus extra for garnish)\nSalt and pepper (to your preference)"
        }
      ]
    },
    {
      "role": "assistant",
      "content": [
        {
          "type": "text",
          "text": "{\n  \"Calories\": \"1400-1600\",\n  \"Protein\": \"80-90 g\",\n  \"Fat\": \"70-80 g\",\n  \"Carbohydrates\": \"110-120 g\"\n}"
        }
      ]
    },
    {
      "role": "user",
      "content": [
        {
          "type": "text",
          "text": str(ingredients)
        }
      ]
    }
    ]


    response = client.chat.completions.create(
        messages=messages,
        model="gpt-4o-mini",
        temperature=1,
        max_tokens=200,
        top_p=1,
        response_format={"type": "json_object"},
        #stop=None
    )

    jdata = response.choices[0].message.content

    # JSON-Daten in ein Python-Wörterbuch umwandeln
    data = json.loads(jdata)

    # Füge die Überschrift und den Absatz hinzu
    html_output = f"<h2>Estimated Nutrition</h2>\n<p>Estimated nutrition for the whole recipe <i>(without optional ingredients)</i>:</p>\n"

    # Füge die ungeordnete Liste hinzu
    html_output += "<ul class='ingr'>\n"
    for key, value in data.items():
        html_output += f"<li><strong>{key}:</strong> {value}</li>\n"
    html_output += "</ul>\n"

    # Füge die handgezeichnete Linie hinzu
    html_output += '<div class="hr--handdrawn"></div>\n'

    # Ergebnis ausgeben
    return html_output

def get_worksheet(account):
    if account not in ACC_CONFIG:
        raise ValueError(f"Account '{account}' not found in ACC_CONFIG")

    # Authenticate and create the gspread client
    auth.authenticate_user()
    creds, _ = default()
    gclient = gspread.authorize(creds)

    # Open the specific worksheet for the account
    sheet_key = ACC_CONFIG[account]['sheet_key']
    worksheet_name = ACC_CONFIG[account]['worksheet_name']
    worksheet = gclient.open_by_key(sheet_key).worksheet(worksheet_name)

    return worksheet

def process_account(account):
    worksheet = get_worksheet(account)
    expected_headers = worksheet.row_values(1)
    rows = worksheet.get_all_records(expected_headers=expected_headers)
    return rows, worksheet

# Define a configuration for multiple accounts
ACC_CONFIG = {
    'account1': {
        'sheet_key': '1_BX7iGx68vvzgR-QCHGhQZtVRogeSzxCD8Ze4MTN3Tc',
        'worksheet_name': 'xmas'
    },
    'account2': {
        'sheet_key': '1Eg6oZ4QM61J3vLKWori0VWExL3IzSwMZ2sdR3cuPR2M',
        'worksheet_name': '1'
    },
    'account3': {
        'sheet_key': '1zX1u3oAjVmvDlc56_R5MM6YZNlujcc2x4wWlnee_yrw',
        'worksheet_name': 's1'
    },
    'account4': {
        'sheet_key': '13jM6Epy2A5d-A-RLFu4DRL4lnCNWf3BLB9wod_vTtZ4',
        'worksheet_name': 's1'
    },
    # Add more accounts as needed
}

def process_image(image_url: str, wp_base_url: str, wp_username: str, wp_password: str) -> str:
    """
    Downloads image from Google Drive and uploads to WordPress.
    
    Args:
        image_url: Source URL of the image (Google Drive)
        wp_base_url: WordPress site base URL
        wp_username: WordPress username
        wp_password: WordPress password
        
    Returns:
        str: WordPress media URL or original URL if processing failed
    """
    try:
        if 'drive.google.com' in image_url:
            file_id = image_url.split('/d/')[1].split('/')[0]
            download_url = f"https://drive.google.com/uc?export=download&id={file_id}"

            response = requests.get(download_url)

            if response.status_code == 200:
                unique_filename = f"image_{uuid.uuid4().hex}.jpg"

                headers = {
                    'Authorization': 'Basic ' + base64.b64encode(f"{wp_username}:{wp_password}".encode()).decode()
                }
                files = {'file': (unique_filename, response.content, 'image/jpeg')}
                wp_upload_url = f"{wp_base_url}wp-json/wp/v2/media"

                upload_response = requests.post(wp_upload_url, headers=headers, files=files)
                if upload_response.status_code == 201:
                    return upload_response.json()['source_url']
                else:
                    print(f"Failed to upload image: {upload_response.text}")
                    return image_url
            else:
                print(f"Failed to download image: {response.text}")
                return image_url
        else:
            return image_url
            
    except Exception as e:
        print(f"Error processing image {image_url}: {str(e)}")
        return image_url

def process_row(row_data: Tuple[int, dict], worksheet, wp_base_url: str, wp_username: str, wp_password: str) -> None:
    i, row = row_data
    
    if not row['url'] and row['img3'] and row['status'] == 'ready for upload':
        try:
            title = row['kw']

            if 'titles' in row and row['titles'].strip():
                titles = row['titles'].split('\n')
                wptitle = random.choice(titles)
            else:
                gwptitle = pintitles(title)
                worksheet.update_cell(i, 4, gwptitle)
                wptitle = gwptitle.split('\n')
                wptitle = random.choice(wptitle)

            image_urls = [row['img1'], row['img2'], row['img3']]

            # Process images concurrently
            with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
                process_image_partial = lambda url: process_image(url, wp_base_url, wp_username, wp_password)
                processed_image_urls = list(executor.map(process_image_partial, image_urls))

            # Update sheet with processed image URLs
            worksheet.update_cell(i, 5, processed_image_urls[0])
            worksheet.update_cell(i, 6, processed_image_urls[1])
            worksheet.update_cell(i, 7, processed_image_urls[2])

            print(f'##### Processing row {i} - Keyword {title}.... ######')

            if row['yt']:
                title1, ingr, steps = summarize_yt(row['yt'])
            elif row['rurl']:
                ingr, steps = genrecipe(row['rurl'])
            else:
                print(f"No valid source for row {i}")
                return

            if steps:
                recipe = htmlsteps(steps)
                htmllist = htmlliste(ingr)
                intro = introgen(title)
                htable = table(title, steps)
                serving_suggestions = generate_serving_suggestions(title, ingr)
                nutrition = nutritionestimate(ingr)

                intro += f'\n<br><br><img src="{processed_image_urls[0]}" alt="{title}" />\n<div class="hr--handdrawn"></div>\n'
                article = ''.join([intro, serving_suggestions, htable, nutrition, htmllist, recipe])
                for img_url in processed_image_urls[1:]:
                    article += f'\n<img src="{img_url}" alt="{title}" />'

                article_url = upload_to_wordpress(article, wp_base_url, wp_username, wp_password, wptitle)

                if article_url:
                    worksheet.update_cell(i, 8, article_url)
                    worksheet.update_cell(i, 9, 'ready for pin')
                else:
                    worksheet.update_cell(i, 11, f"Failed to upload article for {title}")

        except Exception as e:
            print(f"Error processing row {i}: {str(e)}")
            worksheet.update_cell(i, 11, f"Error: {str(e)}")

def main():
    # Display available accounts
    print("Available accounts:")
    for account in ACC_CONFIG.keys():
        print(f"- {account}")

    # Get user input for account selection
    while True:
        selected_account = input("Enter the account you want to process: ").strip()
        if selected_account in ACC_CONFIG:
            break
        else:
            print(f"Invalid account. Please choose from: {', '.join(ACC_CONFIG.keys())}")

    # Process the selected account
    rows, worksheet = process_account(selected_account)

    print(f"Processing account: {selected_account}")

    # Rest of your main function...
    wp_base_url = "https://mollyshomeguide.com/"
    wp_username = "Molly"
    wp_password = "IKmp BLN2 qFH3 sz8R vv9k kAwk"

    # Process rows concurrently
    # Create a list of row data with indices
    row_data = list(enumerate(rows, start=2))
    
    # Process rows concurrently using ThreadPoolExecutor
    max_workers = 3  # Adjust this number based on your needs
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Create partial function with fixed parameters
            process_row_partial = lambda x: process_row(x, worksheet, wp_base_url, wp_username, wp_password)
            
            # Submit all tasks and wait for completion
            futures = [executor.submit(process_row_partial, rd) for rd in row_data]
            
            # Wait for each future to complete
            for future in concurrent.futures.as_completed(futures):
                try:
                    future.result()  # Get the result (or exception)
                except Exception as e:
                    print(f"Task failed: {str(e)}")
if __name__ == "__main__":
    main()