import os
import openai
import requests
from bs4 import BeautifulSoup

apikey = open("apikey.txt", "r")
openai.api_key = apikey.read()

#symptom_list = input("What are your symptoms?")

#symptom_list = "diarrhea, bleeding, stomach pain"
#symptom_list = "shortness of breath, fever, fatigue, dry cough"
#symptom_list = "headache, vomiting, fatigue"

def draft_response(symptoms, gpt_model = "gpt-4"):
    """
    Parameters:
    symptoms: A list of symptoms input as a string, likely written by the end-user from input() in the draft or output by the front end in the final.
    model: the keyword of the LLM used (we're only using "chat" models for now). Tested ones include gpt-3.5-turbo and gpt-4.
    Returns:
    response: A response output by a GPT model giving a "draft response" of different possible diagnoses, as a Python string.
    """

    lead_text = """
    You are a medical student studying general practice.
    Answer the following question in-character for a smart, highly accurate medical student who thinks about their answers carefully before responding.
    Since you're not talking to a patient, but to the doctor examining you, you do not need to include lengthy disclaimers about the need to consult doctors; the doctor knows this.
    Give a list of the five most likely possible diagnoses for the patient given the following symptoms:

    """
    end_text = """
    
    Take a deep breath and then state the obvious possible diagnoses, starting with the most probable. Take the base rates into account: when you hear hoof beats, guess that it's horses and not zebras. Be sure to give short
    responses that mostly just contain the diagnosis. You don't need to add fluff; this is in the next section of the question that you're not answering yet.
    """


    prompt = lead_text + symptoms + end_text

    #print(prompt)
    message=[{"role": "user", "content": prompt}]
    response = openai.ChatCompletion.create(
        model=gpt_model,
        messages = message,
        temperature=0.2,
        max_tokens=1000,
        frequency_penalty=0.0
    )
    return response["choices"][0]["message"]["content"]

def format_diagnosis_list(diagnoses, gpt_model = "gpt-3.5-turbo"):
    """
    Parameters:
    diagnoses: A GPT-generated output containing a list of diagnoses in a Python string in whatever format (i.e. output from draft_response).
    model: the keyword of the LLM used (we're only using "chat" models for now). Tested ones include gpt-3.5-turbo and gpt-4.
    Returns:
    response: A Python list of possible diagnoses.
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
        model=gpt_model,
        messages = message,
        temperature=0.2,
        max_tokens=1000,
        frequency_penalty=0.0
    )
    return [x[3:] for x in response["choices"][0]["message"]["content"].split("\n")]

def format_link_list(disease, gpt_model = "gpt-4"):
    """
    Parameters:
    disease: the name of a disease (an element from  the format_diagnosis_list list - loop over that).
    model: the keyword of the LLM used (we're only using "chat" models for now). Tested ones include gpt-3.5-turbo and gpt-4.
    Returns:
    response: A list of links to sources on the disease, as a Python list.
    """
    lead_text = """
    You are an expert research librarian at a top-ranked medical school.
    A professor has come and requested the best five Internet sources on """ + disease + """ that you have.
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
        model=gpt_model,
        messages = message,
        temperature=0.2,
        max_tokens=1000,
        frequency_penalty=0.0
    )
    #print(response["choices"][0]["message"]["content"])
    return response["choices"][0]["message"]["content"].split("\n")

def format_scrape(link, gpt_model = "gpt-3.5-turbo-16k"):
    """
    Parameters:
    link: a link discussing a disease. (an element from the format_link_list list - loop over that).
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
                    temperature=0.2,
                    max_tokens=1000,
                    frequency_penalty=0.0
                )
                finished_completion = True
            except openai.error.InvalidRequestError:
                response = "Defective"
                finished_completion = True
        if response != "Defective":
            return response["choices"][0]["message"]["content"]
        else:
            return response

def compile_response(symptoms, disease, source, gpt_model = "gpt-3.5-turbo"):
    """
    Parameters:
    symptoms: A list of symptoms input as a string, likely written by the end-user from input() in the draft or output by the front end in the final. (i.e. the first thing passed to draft_response)
    disease: the name of a disease. (i.e. something passed into format_link_list, or output in the list from format_diagnosis_list)
    source: A Web source describing the disease (i.e. output from a format_scrape call that isn't Defective)
    model: the keyword of the LLM used (we're only using "chat" models for now). Tested ones include gpt-3.5-turbo and gpt-4.
    Returns:
    response: A response output by a GPT model giving a "draft response" of different possible diagnoses.
    """

    """
    You are a medical researcher and expert in all sorts of diseases. You are currently working on a paper on effective communication strategies for doctors.
    Your assistant has presented you with a series of symptoms found in the literature, a possible disease associated with those symptoms, and a reputable Internet source
    on this disease. The case report mentioned that the patient was experiencing """ + symptoms + """, and your assistant thinks the cause may be """ + disease + """. Your assistant has attached a resource on """ + disease + """ as follows:

    """
    """

    Since you're not talking to a patient, but discussing a patient in the literature for a paper, you do not need to include lengthy disclaimers about the need to consult doctors; your assistant knows this. However, you should
    not write your response as if addressed to your assistant. Instead, since this is a paper on communication strategies, you should address your response as if it was to the patient in the literature. Still be sure to use a brief
    and fairly informal communication style.

    Take a deep breath and then find out whether your assistant's assessment of the disease makes sense, given the reported symptoms and the web resource about the disease. If not, say "I'm sorry; according to the websites,
    this disease wasn't quite what you have." If so, give a short response that is faithful the web resource in a way that is easily readable by a layperson. There is no need to start with a formal introduction or end with a formal salutation.
    
    """
    lead_text = """
    You are a medical student studying general practice.
    Answer the following question in-character for a smart, highly accurate medical student who thinks about their answers carefully before responding.
    Since you're not talking to a patient, but to the doctor examining you, you do not need to include lengthy disclaimers about the need to consult doctors; the doctor knows this.
    A patient has approached you with the following symptoms: """ + symptoms + """, and the patient thinks the cause might be """ + disease + """. At first, you also think this makes sense.
    Is this consistent with the following web resource on """ + disease + """?

    """


    end_text = """
    Take a deep breath and then briefly explain, as if to this patient, why this disease does or does not make sense as a possibility. Mention other possible symptoms of the disease the patient could look at to confirm or reject this hypothesis.
    """
    prompt = lead_text + source + end_text

    #print(prompt)
    message=[{"role": "user", "content": prompt}]
    response = openai.ChatCompletion.create(
        model=gpt_model,
        messages = message,
        temperature=0.4,
        max_tokens=1000,
        frequency_penalty=0.0
    )
    return response["choices"][0]["message"]["content"]

if __name__ == "__main__":
    symptom_list = input("What are your symptoms?")
    draft = draft_response(symptom_list)
    disease_list = format_diagnosis_list(draft)
    print("Possible diseases:")
    for x in disease_list:
        print(x)
    for disease in disease_list:
        links = format_link_list(disease)
        print("Possible sources on " + disease + ":")
        for x in links:
            print(x)
        website = ""
        for link in links:
            print("Testing a website")
            website = format_scrape(link)
            if website != "Defective":
                print("Website found!")
                break
        if website != "Defective":
            compiled_output = compile_response(symptom_list, disease, website)
            print(compiled_output)
        





"""

test_symptoms = "shortness of breath, fever, fatigue, dry cough"
test_disease = "Pneumonia"
test_resource = "Pneumonia - Symptoms and causes - Mayo Clinic\n\nPneumonia and your lungs\nMost pneumonia occurs when a breakdown in your body's natural defenses allows germs to invade and multiply within your lungs. To destroy the attacking organisms, white blood cells rapidly accumulate. Along with bacteria and fungi, they fill the air sacs within your lungs (alveoli). Breathing may be labored. A classic sign of bacterial pneumonia is a cough that produces thick, blood-tinged or yellowish-greenish sputum with pus.\n\nPneumonia is an infection that inflames the air sacs in one or both lungs. The air sacs may fill with fluid or pus (purulent material), causing cough with phlegm or pus, fever, chills, and difficulty breathing. A variety of organisms, including bacteria, viruses and fungi, can cause pneumonia.\nPneumonia can range in seriousness from mild to life-threatening. It is most serious for infants and young children, people older than age 65, and people with health problems or weakened immune systems.\n\nSymptoms\nThe signs and symptoms of pneumonia vary from mild to severe, depending on factors such as the type of germ causing the infection, and your age and overall health. Mild signs and symptoms often are similar to those of a cold or flu, but they last longer.\nSigns and symptoms of pneumonia may include:\n\nChest pain when you breathe or cough\nConfusion or changes in mental awareness (in adults age 65 and older)\nCough, which may produce phlegm\nFatigue\nFever, sweating and shaking chills\nLower than normal body temperature (in adults older than age 65 and people with weak immune systems)\nNausea, vomiting or diarrhea\nShortness of breath\n\nNewborns and infants may not show any sign of the infection. Or they may vomit, have a fever and cough, appear restless or tired and without energy, or have difficulty breathing and eating.\n\nCauses\nMany germs can cause pneumonia. The most common are bacteria and viruses in the air we breathe. Your body usually prevents these germs from infecting your lungs. But sometimes these germs can overpower your immune system, even if your health is generally good.\nPneumonia is classified according to the types of germs that cause it and where you got the infection.\nCommunity-acquired pneumonia\nCommunity-acquired pneumonia is the most common type of pneumonia. It occurs outside of hospitals or other health care facilities. It may be caused by:\n\nBacteria. The most common cause of bacterial pneumonia in the U.S. is Streptococcus pneumoniae. This type of pneumonia can occur on its own or after you've had a cold or the flu. It may affect one part (lobe) of the lung, a condition called lobar pneumonia.\nBacteria-like organisms. Mycoplasma pneumoniae also can cause pneumonia. It typically produces milder symptoms than do other types of pneumonia. Walking pneumonia is an informal name given to this type of pneumonia, which typically isn't severe enough to require bed rest.\nFungi. This type of pneumonia is most common in people with chronic health problems or weakened immune systems, and in people who have inhaled large doses of the organisms. The fungi that cause it can be found in soil or bird droppings and vary depending upon geographic location.\nViruses, including COVID-19. Some of the viruses that cause colds and the flu can cause pneumonia. Viruses are the most common cause of pneumonia in children younger than 5 years. Viral pneumonia is usually mild. But in some cases it can become very serious. Coronavirus 2019 (COVID-19) may cause pneumonia, which can become severe.\n\nHospital-acquired pneumonia\nSome people catch pneumonia during a hospital stay for another illness. Hospital-acquired pneumonia can be serious because the bacteria causing it may be more resistant to antibiotics and because the people who get it are already sick. People who are on breathing machines (ventilators), often used in intensive care units, are at higher risk of this type of pneumonia.\n\nHealth care-acquired pneumonia\nHealth care-acquired pneumonia is a bacterial infection that occurs in people who live in long-term care facilities or who receive care in outpatient clinics, including kidney dialysis centers. Like hospital-acquired pneumonia, health care-acquired pneumonia can be caused by bacteria that are more resistant to antibiotics.\n\nAspiration pneumonia\nAspiration pneumonia occurs when you inhale food, drink, vomit or saliva into your lungs. Aspiration is more likely if something disturbs your normal gag reflex, such as a brain injury or swallowing problem, or excessive use of alcohol or drugs.\n\nRisk factors\nPneumonia can affect anyone. But the two age groups at highest risk are:\n\nChildren who are 2 years old or younger\nPeople who are age 65 or older\n\nOther risk factors include:\n\n"
print(compile_response(test_symptoms, test_disease, test_resource)["choices"][0]["message"]["content"])
"""

