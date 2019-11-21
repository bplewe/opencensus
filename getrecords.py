import requests, re, csv
lasted = "https://integration.familysearch.org/platform/records/waypoints/9BQK-9LN:1030550201,1030789001,1030798601?cc=1325221"
 
outfile = open("households.csv","a")
fields = ["uuid","edname","page","hhid","lineNbr","headname","hhurl","imageurl","hhsize","genders","marstats","races","birthdates","birthplaces","immigrations","ages","relationships","fatherbps","motherbps"]
writing = csv.DictWriter(outfile, fieldnames=fields,lineterminator='\n')
writing.writeheader()

hdr = {'accept': 'application/json'}

def getvalue(obj) :
    value = ""
    for valrow in obj["values"]:
        if valrow["type"]=="http://gedcomx.org/Interpreted":
            value = valrow["text"]
        if value == "" and valrow["type"]=="http://gedcomx.org/Original":
            value = valrow["text"]
    return value

def getrecords(reclisturl): #given a URL of an image record, list all of the records within it
    recs = requests.get(reclisturl, headers=hdr).json().get("sourceDescriptions")
    if (recs):
        for rec in recs:
            recid = rec["id"]
            recurl = rec["links"]["record"]["href"]
    #        print("        " + recurl)
            recobj = requests.get(recurl, headers=hdr).json()
    #        print(recobj)

            name = ""
            lineNbr=""
            hhid=""
            uuid=""
            imageurl=reclisturl
            hhsize = 0
            gender = []
            marstatus = []
            race = []
            birthdate = []
            birthplace = []
            immigration = []
            age = []
            relationship = []
            fatherbp = []
            motherbp = []

            person = recobj["persons"][0] #head of household
            if "names" in person:
                namerec = person["names"][0]
                if (namerec["type"] == "http://gedcomx.org/BirthName"):
                    name = namerec["nameForms"][0]["fullText"]
            f = person["fields"]
            for row in f:
                rowtype = row["type"].replace("http://familysearch.org/types/fields/","")
                val = row["values"][0]["text"]
                if rowtype == "SourceLineNbr":
                    lineNbr = val
                if rowtype == "HouseholdId":
                    hhid = val
                if rowtype == "UniqueIdentifier":
                    uuid = val
                if rowtype == "ImageNbr":
                    page = val
                if rowtype == "ImageArk":
                    imageurl = val

            for person in recobj["persons"]:
                hhsize += 1
                if "gender" in person:
                    gender.append(getvalue(person["gender"]["fields"][0]))
                for fact in person["facts"]:
                    #    shortfact = getvalue(fact)
                    #    print(shortfact)
                    field = fact["type"].replace("http://gedcomx.org/", "")
                    # print(field+" " +str(fact.keys()))
                    if field == "MaritalStatus":
                        marstatus.append(getvalue(fact["fields"][0]))
                    if field == "Race":
                        race.append(getvalue(fact["fields"][0]))
                    if field == "Birth":
                        if "date" in fact:
                            birthdate.append(getvalue(fact["date"]["fields"][0]))
                        if "place" in fact:
                            birthplace.append(getvalue(fact["place"]["fields"][0]))
                    if field == "Immigration":
                        if "date" in fact:
                            immigration.append(getvalue(fact["date"]["fields"][0]))

                for fact in person["fields"]:
                    field = fact["type"].replace("http://gedcomx.org/", "")
                    # print(field+" " +str(fact.keys()))
                    if field == "Age":
                        age.append(getvalue(fact))
                    if field == "RelationshipToHead":
                        relationship.append(getvalue(fact))
                    if field == "FatherBirthPlace":
                        fatherbp.append(getvalue(fact))
                    if field == "MotherBirthPlace":
                        motherbp.append(getvalue(fact))

            writing.writerow({"headname": name, "hhurl": recurl, "imageurl":imageurl, "edname":edname, "page":page, "lineNbr":lineNbr,
                              "hhid":hhid,"uuid":uuid,"hhsize":hhsize, "genders":gender,"marstats":marstatus,"races":race,"birthdates":birthdate,
                              "birthplaces":birthplace,"immigrations":immigration,"ages":age,"relationships":relationship,
                              "fatherbps":fatherbp,"motherbps":motherbp})

def getimage(imgurl):
    imgobj = requests.get(imgurl, headers=hdr).json()

    cite = imgobj["sourceDescriptions"][0]["citations"][0]["value"]
    loc = re.sub(r";.+", "", re.sub(r".+2014\), ", "", cite))
    print("    " + loc + ": " + imgurl)
    # Image URL is not available in anonymous access
    # imgurl = imgobj["links"]["image-stream-image-dist"]["href"]
    # print("  "+imgurl)

    recsurl = imgobj["links"]["records"]["href"].replace("www.","integration.")
    print("      "+recsurl)
    getrecords(recsurl)

def getedimages(edurl):
    global page
    page = 1
    edrec = requests.get(edurl,headers=hdr).json().get("sourceDescriptions")
    for rec in edrec:
        if ("resourceType" in rec) and ("identifiers" in rec):
            rt = rec["resourceType"]
            if (rt=="http://gedcomx.org/DigitalArtifact"):
                imgurl = rec["identifiers"]["http://gedcomx.org/Primary"][0].replace("ark:/61903","platform/records/images")
                getimage(imgurl)
                page += 1

def getcountyimages(resurl):
    global edname
    print(resurl)
    catchup = 0
    countyrec = requests.get(resurl,headers=hdr).json().get("sourceDescriptions")
    for rec in countyrec:
        if ("titleLabel" in rec) and ("titles" in rec):
            edname = rec["titles"][0]["value"]
            t = rec["titleLabel"]["value"]
            if (t=="Enumeration District"):
                edurl = rec["identifiers"]["http://gedcomx.org/Primary"][0]
                print("  "+edname+": "+edurl)
                if edurl == lasted:
                    catchup = 1
                if catchup == 1:
                    getedimages(edurl)
                else:
                    print("done")


countyurl = "https://integration.familysearch.org/platform/records/waypoints/9BQK-92S?cc=1325221"
url = "https://www.familysearch.org/platform/records/images/3:1:S3HT-DZ2Q-68B"
getcountyimages(countyurl)

outfile.flush()
outfile.close()
