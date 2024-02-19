import cv2
import time
import sqlite3
import hashlib
import numpy as np
from PIL import Image
import streamlit as st
import tensorflow as tf
import tensorflow_hub as hub
import matplotlib.pyplot as plt
from keras.models import Sequential, load_model

hideMenuStyle = """
	<style>
	#MainMenu {visibility: hidden; }
	footer {visibility: hidden; }
	</style>
	"""
st.markdown(hideMenuStyle, unsafe_allow_html=True)

imageSize = 256

def imageUploader():
    st.subheader("Upload an MR Image")
    imageUploaded = st.file_uploader(
        "", type=['jpg', 'png', 'jpeg'])
    if imageUploaded is not None:
        image = Image.open(imageUploaded)
        prediction = predictTumour(image)

        columnOne, columnTwo = st.columns(2)
        columnOne.header("MR Image")
        columnOne.image(image, use_column_width=True)

        columnTwo.header("Predection")
        columnTwo.subheader(prediction)


def predictTumour(image):
    CATEGORIES = ["no", "yes"]

    processedImage = image.resize((255, 255))
    processedImage = np.array(processedImage)
    processedImage = cv2.cvtColor(processedImage, cv2.COLOR_BGR2GRAY)
    processedImage = tf.keras.preprocessing.image.img_to_array(processedImage)
    processedImage = processedImage / 255.0
    processedImage = np.expand_dims(processedImage, axis=0)

    shape = ((255, 255, 1))

    # if this path doesnot work for you modify it where you have saved tyhe model (/home/user/path-to-savedModel)
    classifier = load_model("../Model/custom-model.h5")
    model = Sequential(
        [hub.KerasLayer(classifier, input_shape=shape)])

    prediction = model.predict(processedImage)
    scores = tf.nn.softmax(prediction[0])
    scores = scores.numpy()
    index = np.argmax(scores)

    imageClass = CATEGORIES[index]
    probability = round(scores[index] * 100, 2)

    with st.spinner('"The process is evolving. please be patient...."'):
        time.sleep(3)
    if imageClass == 'yes':
        return (f"Seems {probability} probability of having Tumour")

    elif imageClass == 'no':
        return (f"Seems {probability} probability of having no Tumour")

    else:
        return ("Image unidentified")

def makeHashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()


def checkHashes(password, hashedText):
    if makeHashes(password) == hashedText:
        return hashedText
    return False


conn = sqlite3.connect('data.db')
cursor = conn.cursor()


def createUserTable():
    cursor.execute(
        'CREATE TABLE IF NOT EXISTS userstable(username TEXT,password TEXT)')


def addUserData(username, password):
    cursor.execute('INSERT INTO userstable(username,password) VALUES (?,?)',
                   (username, password))
    conn.commit()


def loginUser(username, password):
    cursor.execute('SELECT * FROM userstable WHERE username =? AND password = ?',
                   (username, password))
    data = cursor.fetchall()
    return data


def main():
    st.title("BRAIN TUMOUR CLASSIFIER")

    menu = ["SignUp", "Login"]
    choice = st.sidebar.selectbox("", menu)

    if choice == "Login":

        username = st.sidebar.text_input("User Name")
        password = st.sidebar.text_input("Password")
        if st.sidebar.checkbox("Login"):
            createUserTable()
            hashedPassword = makeHashes(password)

            result = loginUser(username, checkHashes(password, hashedPassword))

            if result:
                imageUploader()
            else:
                st.warning("Incorrect Username/Password")

    elif choice == "SignUp":
        st.subheader("Create New Account")
        newUser = st.text_input("Username")
        newPassword = st.text_input("Password", type='password')

        if st.button("Signup"):
            createUserTable()
            cursor.execute(
                'SELECT * FROM userstable WHERE username=?', (newUser,))
            data = cursor.fetchall()

            if len(data) == 1:
                st.write("User Already exist")

            elif newUser == "" or newPassword == "":
                st.warning("Fields cannot be empty")

            else:
                addUserData(newUser, makeHashes(newPassword))
                st.success("You have successfully created a valid Account")
                st.info("Go to Login Menu to login")


if __name__ == '__main__':
    main()
