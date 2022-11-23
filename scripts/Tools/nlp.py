import nltk
import ssl
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context


nltk.download('averaged_perceptron_tagger')
nltk.download('tagsets')
nltk.download("punkt")
nltk.download('words')
import spacy
import re
from spacy import displacy
from collections import Counter

from nltk.corpus import stopwords,words
from nltk.tokenize import word_tokenize
#NER = spacy.load("en_core_web_sm")
ner = spacy.load("en_core_web_sm") #to use this please download zipped version and install via pip
stops = set(stopwords.words('english'))


# text = "Each week the NZ Herald and Newstalk ZB's Cooking the Books podcast tackles a different money problem. Today, it's how to detangle the housing situation and make the most of it. Hosted by Frances Cook.The housing market is one where there's always winners and losers. Buyers want low prices, owners want high prices, so whatever market forces are at play someone usually ends up disappointed.The problem is right now, things are so uncertain.We do have early indicators to help us read the tea leaves. The latest figures are for March, which take us just six days into lockdown, and it's already looking rough out there. National house sale data from the Real Estate Institute shows we've hit a nine year low, with the numbers of houses for sale down almost five percent. When figures come out showing the rest of the lockdown it's unlikely to get any prettier, but the real question is what will happen when lockdown lifts. We just don't know.However whether you're a buyer or a seller, I'm a big believer that no matter what the situation is there are always things you can do to get the odds in your favour. For the latest Cooking the Books, I talked to OneRoof editor Owen Vaughan.We discussed whether this might be an opportunity for first home buyers, the tactics that can help sellers get a better price, and what key indicators to watch for as we leave lockdown.If you have a question about this podcast, or question you'd like answered in the next one, come and talk to me about it. I'm on Facebook here https://www.facebook.com/FrancesCookJournalist/ Instagram here https://www.instagram.com/francescooknz/ and Twitter here https://twitter.com/FrancesCook"
# text = "Each week the NZ Herald and Newstalk ZB's Cooking the Books podcast tackles a different money problem. Today, it's why all investments need a certain amount of safety, and how to organise that. Hosted by Frances Cook.All but the most blinkered of politicians and property lobbyists admit we have a housing crisis in this country. Prices are climbing far faster than wages, and as a result some people worry they'll never be able to buy their own home. One interesting solution to bring prices back down is to increase prefab housing. Think of it like this. It's always more expensive to create something bespoke, in place, and bring all the workers to that spot to get it done. That's how most of our housing is done right now. Whereas prefab is exactly what the name says - it's pre-made, elsewhere, usually in a factory. The workers get into a groove, get most of the parts done in an efficient factory model, and then ship them to the housing site to be assembled. So why don't we have lots more of this happening? Well, there's been some red tape that has made this extremely difficult in New Zealand. As always though, you just need to know the pathways around it. For the latest Cooking the Books podcast I talked to Scott Fisher from PreFabNZ, and Rupert Gough from Mortgage Lab. We discussed what's caused problems for prefab so far, which banks are friendliest to it, and what types of law changes are in the works. If you have a question about this podcast, or question you'd like answered in the next one, come and talk to me about it. I'm on Facebook here https://www.facebook.com/FrancesCookJournalist/ Instagram here https://www.instagram.com/francescooknz/ and Twitter here https://twitter.com/FrancesCook"
# text = "Each week the NZ Herald and Newstalk ZB's Cooking the Books podcast tackles a different money problem. Today, it's the first steps you can take if you've lost your job. Hosted by Frances Cook.We're in tough times, and the sad reality is that many of us are losing our jobs. If you're coupled up and one of you loses your job, it's a different type of difficult as there's less safety net. You can't get the same support from Work and Income, as your partner's salary will be taken into account. But there are other things you can do to make the most of the one income you still have. You can stabilise your finances to give you breathing space to make it through this difficult time. For the latest Cooking the Books I talked to Tony Agar from Hamilton Budgeting Advisory Trust.We talked about the support available from Government and community groups, where to start in setting up and cutting back a budget, and what to do if you have any debts. For the podcast, listen on the player at the top of the article. If you have a question about this podcast, or question you'd like answered in the next one, come and talk to me about it. I'm on Facebook here https://www.facebook.com/FrancesCookJournalist/ Instagram here https://www.instagram.com/francescooknz/ and Twitter here https://twitter.com/FrancesCook"
text = "Each week the NZ Herald and Newstalk ZB's Cooking the Books podcast tackles a different money problem. Today, it's what you should expect from the housing market, and how to adapt to it. Hosted by Frances Cook.Your house may be your castle, but it's also the biggest investment many of us will make, and it comes with the commitment of mortgage debt. So as we try to ride out the severe shockwaves from Covid-19, you won't be surprised to learn the current situation is also a gamechanger for housing. For one thing, unemployment is going up, and every time that happens house prices tend to go down.With tourism stopped, AirBnB is a nonstarter. Many former hosts are either switching to go into the long-term rental market, or opting out entirely and putting the property up for sale. Either of those would be a big force for change on their own, but now we have that and many other issues forcing change all at the same time.So let's rip the bandaid off and start with the bad news, although I promise there is some good news in this, so stick with us. For the latest Cooking the Books I talked to Herald property editor Anne Gibson. We discussed what's happening with housing in lockdown, what experts are forecasting for the future, and what this means for both first home buyers and current property owners. If you have a question about this podcast, or question you'd like answered in the next one, come and talk to me about it. I'm on Facebook here https://www.facebook.com/FrancesCookJournalist/ Instagram here https://www.instagram.com/francescooknz/ and Twitter here https://twitter.com/FrancesCook"
def nlp_routine(old_text):
    instruments = []
    text = ""
    lst = old_text.split(" ")
    for e in lst:
        #print(e)
        if e.lower() in words.words():
           # print("here")
            text = text+e.lower()
            text  = text + " "
    text = re.sub(r'\w+:\/{2}[\d\w-]+(\.[\d\w-]+)*(?:(?:\/[^\s/]*))*', '', text)
    text_tokens = word_tokenize(text.lower())
    text = [word for word in text_tokens if not word in stopwords.words() and word.isalnum()]
    text = " ".join(text)
    print(text)
    instruments = instruments + text.split(" ")
    # doc = nltk.pos_tag(text.split())
    # my_set = []

    # print(text)
    # doc = ner(text)

    # for ent in doc.ents:
    #     print("here")
    #     print(ent.text, ent.start_char, ent.end_char, ent.label)

    # named_entities = []
    # money_entities = []
    # organization_entities = []
    # location_entities = []
    # time_indicator_entities = []

    # # # PERSON : Denotes names of people
    # # # GPE : Denotes places like counties, cities, states.
    # # # ORG : Denotes organizations or companies
    # # # WORK_OF_ART : Denotes titles of books, fimls,songs and other arts
    # # # PRODUCT : Denotes products such as vehicles, food items ,furniture and so on.
    # # # EVENT : Denotes historical events like wars, disasters ,etc…
    # # # LANGUAGE : All the recognized languages across the globe.
    # print(text)
    # print("!"*50)
    # text1= ner(text)
    # # print(text1)
    # # # spacy.explain("DATE")
    # # # spacy.explain("MONEY")

    # for word in text1.ents:
    #     print(word)
    #     # print(word.text,word.label_)
    #     label = word.label_
    #     entity = word.text
    #     print("#################################")
    #     print(word)
    #     print(label)

    #     # if label in ["TIM", "DATE"]:
    #     #     time_indicator_entities.append(entry)
    #     # # money value entities detection
    #     # elif label in ["MONEY"]:
    #     #     money_entities.append(entry)
    #     # # organization entities detection
    #     if label in ["ORG"]:
    #          organization_entities.append(entity)
    #     # # Geographical and Geographical entties detection
    #     # elif label in ["GPE", "GEO"]:
    #     #     location_entities.append(entry)
    #     # # extract artifacts, events and natural phenomenon from text
    #     if label in ["PERSON"]:#"ART", "EVE", "NAT", 
    #         # print(entity)
    #         # print("here")
    #         for w in entity.split():
    #             # print(w)
    #             entity = entity.replace(w, w.capitalize())
    #             # print(entity)
    #         named_entities+=[entity]
    return instruments



def main():
    nlp_routine(text)

if __name__ == '__main__':
    main()