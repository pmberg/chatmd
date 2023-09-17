from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from mygpt import gptbackend
from fastapi.responses import StreamingResponse

app = FastAPI()

origins = [
    "http://localhost:3000",  # React app address
    "http://127.0.0.1:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Symptoms(BaseModel):
    symptoms: str


# This function will generate streamed responses.
# This is just a basic example and you would need to structure this to match your actual logic.
def stream_diagnosis(data: Symptoms):
    possible_diagnoses = gptbackend.draft_response(data.symptoms)

    # GIVES OUT STR OF 5 GUESSES
    yield possible_diagnoses # this will be your first streamed response
    print("yielded guesses")
    print(possible_diagnoses)

    diagnosis_list = gptbackend.format_diagnosis_list(possible_diagnoses)
    # GIVES OUT LIST OF 5 GUESSES AS STR
    clarification_question = gptbackend.ask_for_clarifier(data.symptoms, possible_diagnoses)
    yield str(clarification_question) # another response # TODO: MAKE THIS BASED ON CHATGPT

    yield_count = 0
    for diagnosis_list_item in diagnosis_list: # ITERATE OVER 5 GUESSES
        links_list = gptbackend.format_link_list(diagnosis_list_item) # GET 5 WEBSITES FOR EACH
        #yield str(links_list)
        print(links_list)
        defect = 0
        for item in links_list:
            scrp = gptbackend.format_scrape(item)


            if scrp == "Defective":
                print("defective link")
                defect += 1
                if defect == 5:
                    print("all links defective")
                    yield "No links found"
                    yield "No final response"
                    yield_count += 2
                    print("yield count: " + str(yield_count))
                continue
            else:
                print("found working link: " + str(item))
                final_response_for_guess = gptbackend.compile_response(data.symptoms, diagnosis_list_item, scrp)
                final_score = gptbackend.get_score(data.symptoms, diagnosis_list_item, scrp)
                print("final score: " + str(final_score))

                yield final_score
                yield final_response_for_guess # this will be your final streamed response
                yield_count += 2
                print("yield count: " + str(yield_count))
                break


# POST endpoint to start the diagnosis process and return initial results
@app.post("/diagnose/request")
async def diagnose_request(data: Symptoms):
    possible_diagnoses = gptbackend.draft_response(data.symptoms)
    # For now, just return the initial diagnoses, we'll handle streaming in the other endpoint
    return {"diagnoses": possible_diagnoses}


# GET endpoint for streaming the data
@app.post("/diagnose/stream")
def diagnose_stream(data: Symptoms):
    return StreamingResponse(stream_diagnosis(data), media_type="text/event-stream")




# OUTPUT:
# 5 guesses
# FOLLOW UP Q
# PROBA AND FINAL RES (foreach guess)
