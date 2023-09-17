import os
import openai
import requests
from bs4 import BeautifulSoup

apikey = open("apikey.txt", "r")
openai.api_key = apikey.read()

#symptom_list = input("What are your symptoms?")

symptom_list = "diarrhea, bleeding, stomach pain"

def draft_response(symptoms, gpt_model = "gpt-3.5-turbo"):
    """
    Parameters:
    symptoms: A list of symptoms input as a string, likely written by the end-user from input() in the draft or output by the front end in the final.
    model: the keyword of the LLM used (we're only using "chat" models for now). Tested ones include gpt-3.5-turbo and gpt-4.
    Returns:
    response: A response output by a GPT model giving a "draft response" of different possible diagnoses.
    """

    lead_text = """
    You are a medical student studying general practice.
    Answer the following question in-character for a smart, highly accurate medical student who thinks about their answers carefully before responding.
    Since you're not talking to a patient, but to the doctor examining you, you do not need to include lengthy disclaimers about the need to consult doctors; the doctor knows this.
    Give a list of possible diagnoses for the patient given the following symptoms:

    """
    end_text = """
    
    Take a deep breath and then state the obvious possible diagnoses, starting with the most probable. Take the base rates into account: when you hear hoof beats, guess that it's horses and not zebras.
    """


    prompt = lead_text + symptoms + end_text

    #print(prompt)
    message=[{"role": "user", "content": prompt}]
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages = message,
        temperature=0,
        max_tokens=1000,
        frequency_penalty=0.0
    )
    #print(response["choices"][0]["message"]["content"])
    return response

def format_symptom_list(symptoms, gpt_model = "gpt-3.5-turbo"):
    """
    Parameters:
    symptoms: A list of symptoms input as a string, likely written by the end-user from input() in the draft or output by the front end in the final.
    model: the keyword of the LLM used (we're only using "chat" models for now). Tested ones include gpt-3.5-turbo and gpt-4.
    Returns:
    response: A response output by a GPT model giving a list of symptoms written in a formulaic manner that can easily be searched by a medical API.
    """
    raise NotImplementedError

def format_diagnosis_list(diagnoses, gpt_model = "gpt-3.5-turbo"):
    """
    Parameters:
    diagnoses: A GPT-generated output containing a list of diagnoses in whatever format.
    model: the keyword of the LLM used (we're only using "chat" models for now). Tested ones include gpt-3.5-turbo and gpt-4.
    Returns:
    response: A response output by a GPT model giving a list of symptoms written in a formulaic manner that can easily be searched by a medical API.
    """
    lead_text = """
    You are an expert at parsing text and making ordered lists.
    What follows is an extremely verbose response containing a bunch of diagnoses. Pare them down to a simple format. An example of such a simple format is below:

    1. Lupus
    2. Roundworm
    3. Strep throat
    4. Lymphoma


    The text you should reformat is below:

    
    """
    end_text = """
    Take a deep breath and be sure only to output a neatly formatted ordered list, no boilerplate.    
    """


    prompt = lead_text + diagnoses + end_text

    #print(prompt)
    message=[{"role": "user", "content": prompt}]
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages = message,
        temperature=0,
        max_tokens=1000,
        frequency_penalty=0.0
    )
    #print(response["choices"][0]["message"]["content"])
    return response

def format_link_list(disease, gpt_model = "gpt-3.5-turbo"):
    """
    Parameters:
    disease: the name of a disease.
    model: the keyword of the LLM used (we're only using "chat" models for now). Tested ones include gpt-3.5-turbo and gpt-4.
    Returns:
    response: A list of links to sources on the disease.
    """
    lead_text = """
    You are an expert research librarian at a top-ranked medical school.
    A professor has come and requested the best three Internet sources on """ + disease + """ that you have.
    In particular, these should be Internet sources that can easily be accessed by a web scraper. A homepage for an association for people with """ + disease + """ without much content itself
    would not be good, but a Mayo Clinic, Wikipedia, WebMD, etc. page would be good.
    He is very particular that you output the URLs alone, separated by newlines, with no other text. The format is as follows (using Beatlemania as an example disease):

    https://en.wikipedia.org/wiki/Beatlemania
    https://museumofyouthculture.com/beatlemania/
    https://www.history.com/news/beatlemania-sweeps-the-united-states-50-years-ago
    https://www.theguardian.com/music/2013/sep/29/beatlemania-screamers-fandom-teenagers-hysteria
    https://www.theatlantic.com/photo/2014/05/1964-beatlemania/100745/

    Take a deep breath and be sure only to output a list of relevant URLs separated by newlines, no boilerplate.    
    """


    prompt = lead_text

    #print(prompt)
    message=[{"role": "user", "content": prompt}]
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages = message,
        temperature=0,
        max_tokens=1000,
        frequency_penalty=0.0
    )
    #print(response["choices"][0]["message"]["content"])
    return response

def format_scrape(link, gpt_model = "gpt-3.5-turbo-16k"):
    """
    Parameters:
    link: a link discussing a disease.
    model: the keyword of the LLM used (we're only using "chat" models for now). Tested ones include gpt-3.5-turbo-16k, gpt-3.5-turbo and gpt-4.
    Returns:
    response: A version of the website trimmed of all gibberish. Alternatively, return the text "Defective" if the website didn't scrape.
    """
    lead_text = """
    You are an expert administrative assistant at a top-ranked medical school.
    A professor has approached you with the output of a web scraping script, from a medical website about a disease. The output is as follows.

    """

    end_text = """
    
    Take a deep breath and be sure only to output the content of the website itself, without any boilerplate that was spit out as a byproduct of scraping. Include all content, but not sidebars, topbars, and other scraping artifacts.
    """


    html_output = requests.get(link)
    defective = False
    if html_output.status_code == 200: # HTTP status code 200 means OK
        soup = BeautifulSoup(html_output.content, 'html.parser')
        scrape = soup.get_text() # This prints the entire textual content of the page
    else:
        defective = True
    if defective:
        return "Defective"
    else:
        prompt = lead_text + scrape + end_text

        #print(prompt)

        #print("Got here")
        message=[{"role": "user", "content": prompt}]
        token_count = 1000
        finished_completion = False
        while not finished_completion:
            #print("Made it here")
            try:
                response = openai.ChatCompletion.create(
                    model=gpt_model,
                    messages = message,
                    temperature=0,
                    max_tokens=1000,
                    frequency_penalty=0.0
                )
                finished_completion = True
            except:
                #print("Exception raised")
                if token_count >= 100:
                    token_count -= 100
                else:
                    response = "Defective"
                    finished_completion = True
        #print(response["choices"][0]["message"]["content"])
        return response



"""
response_01 = draft_response(symptom_list)
print("Made a draft response.")
dl_01 = format_diagnosis_list(response_01["choices"][0]["message"]["content"])
diagnosis_list_wnums = dl_01["choices"][0]["message"]["content"].split("\n")
diagnosis_list = [x[3:] for x in diagnosis_list_wnums]

print("Possible diagnoses:")
for x in diagnosis_list:
    print(x)

links_raw=format_link_list(diagnosis_list[2])
list_of_links = links_raw["choices"][0]["message"]["content"].split("\n")

print("Possible resources for " + diagnosis_list[2])
for x in list_of_links:
    print(x)

raw_scraped_links = [format_scrape(x)["choices"][0]["message"]["content"] for x in list_of_links]
scraped_links = [x for x in raw_scraped_links if x != "Defective"]
"""
    

