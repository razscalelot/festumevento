import os
import subprocess
import time
import uuid
directory = 'D:\\PythonProject\\festumevento_project\\festumevento\\media\\buy\\poster\\svg'

changeAmount = "25"
changeType = '₹'
changeText = "On men offer"
for filename in os.listdir(directory):
    if filename.endswith(".svg"):
      #do smth
      print(filename)
      now = time.time()
      #p=subprocess.call(['convert','-density','1200','-resize','800x400',filename,filename+".jpeg"], shell=True)
      print(directory+ "\\" + filename)
      with open(directory+"/"+filename, 'r') as file:
        data = file.read()
        data = str(data)
        #print(data)
        data = data.replace("$Amount$",changeAmount)
        data = data.replace("$type$",changeType)
        data = data.replace("$text$",changeText)     
        #data = data.replace("MEN","No")
        #print(data)
        name = "temp_"+str(uuid.uuid4())+".svg"
        nameOutput = "temp_"+str(uuid.uuid4())+".png"
        f =  open(directory+"/"+name,"w+", encoding='utf-8')
        f.write(data)
        f.close()
        print("svgexport '" + directory + "/" + name + "' '" + directory + "/" + nameOutput + "' 800:400")
        p=subprocess.call(['svgexport',directory+"/"+name,directory+"/"+nameOutput,"800:400"], shell=True)
        later = time.time()
        difference = int(later - now)
        os.remove(name)
        print("Time taken:-"+ str(difference))
     