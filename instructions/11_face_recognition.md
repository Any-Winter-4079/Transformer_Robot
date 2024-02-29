Multi-modal LLMs can assist in identifying famous characters (present in the training data), but for the rest of the people (who will potentially be the robot's interlocutors and are rarely included in the training data), another method is required to collect new faces (i.e., save their images), learn about them (i.e., train a model), and correctly identify them when their face is recollected/captured again.

In this case, the incorporation of [DeepFace](https://github.com/serengil/deepface), a framework that allows the permutation between various backends (for face detection) and models (for face recognition), is studied. In particular, it is decided to use 1054 images (250x250) belonging to the first 432 people (or all with names starting with ‘A’) from the [Labelled Faces in the Wild (LFW) Dataset](https://www.kaggle.com/datasets/jessicali9530/lfw-dataset) (from the total of +13k images and +5.7k people it provides), to compare the performance of OpenCV, SSD, MTCNN, RetinaFace, MediaPipe, YOLOv8, YuNet, and Fast MTCNN as backends (to identify the faces present in the image) and VGG-Face, FaceNet, FaceNet512, OpenFace, DeepID, and ArcFace as recognition models (to identify to whom those faces belong).

It is noteworthy that these models work by generating a representation or embedding of the images (so that new images can be compared with this representation through a similarity metric). Therefore, the speed at which these representations can be created is first studied. Figure 1 shows the number of images (or iterations) that each model can represent as an embedding per second (out of 1024 of the total 1054 images, keeping 30 for tests). As can be observed, DeepID and VGG-Face are - by far - the fastest models. However, once an embedding has been created for a set of images, it is not necessary to recalculate it to add new faces to the dataset of known images (only requiring the calculation of the embedding of new images), which is why all are considered acceptable.

<div align="center">
<img width="500" alt="Screenshot 2024-02-29 at 03 26 13" src="https://github.com/Any-Winter-4079/Transformer_Robot/assets/50542132/bdd27eff-6cad-4356-962f-d4d6cd367685">
<p>Figure 1. Number of images that 6 face recognition models (VGG-Face, Facenet, Facenet512, OpenFace, DeepID, and ArcFace) can convert into embeddings, per second, in DeepFace.</p>
</div>

To study the performance of different backends and models, we can use [1_benchmark_face_recognition_with_known_faces](https://github.com/Any-Winter-4079/Transformer_Robot/blob/main/computer_code/face_recognition/1_benchmark_face_recognition_with_known_faces.py) with 30 images of people present in the embeddings (selecting the last photo of those people, in descending alphabetical order, who have ≥4 images, moving it to the test directory, and removing the image from the 'training' dataset, so it is not stored in the embedding) in order to compare the number of correct predictions and the average time per prediction for different backend-model combinations. It is important to highlight that each model has default thresholds - above which two faces are not considered to be the same person - in DeepFace (see Table 1), and in this first experiment, these default thresholds are used with cosine as the similarity metric. The results are presented in Figure 2.

<div align="center">

| Model       | Cosine | Euclidean | Euclidean L2 |
|-------------|--------|-----------|--------------|
| VGG-Face    | 0.68   | 1.17      | 1.17         |
| Facenet     | 0.40   | 10        | 0.80         |
| Facenet512  | 0.30   | 23.56     | 1.04         |
| ArcFace     | 0.68   | 4.15      | 1.13         |
| Dlib        | 0.07   | 0.6       | 0.4          |
| SFace       | 0.593  | 10.734    | 1.055        |
| OpenFace    | 0.10   | 0.55      | 0.55         |
| DeepFace    | 0.23   | 64        | 0.64         |
| DeepID      | 0.015  | 45        | 0.17         |
<p>Table 1. Default thresholds for each recognition model and similarity metric in DeepFace.</p>
</div>

<div align="center">
  <img width="700" alt="Screenshot 2024-02-29 at 11 42 41" src="https://github.com/Any-Winter-4079/Transformer_Robot/assets/50542132/1aca4ded-c8f1-4fc5-9785-bfb8daf92d5d">
  <p>Figure 2. Number of correct predictions (out of 30) and average time per prediction for 6 models and 8 different backends in DeepFace, with cosine similarity and default thresholds.</p>
</div>

From the figure, it is observed how OpenCV, SSD, MediaPipe, YuNet, and Fast MTCNN are the fastest backends, while in terms of detection numbers, it can be deduced that many have similar performance (MTCNN detects a minimum of 29 faces -for having 29 correct predictions with ArcFace- SSD, YuNet, and Fast MTCNN detect a minimum of 28 faces, YOLOv8 a minimum of 27, OpenCV and RetinaFace at least 26, and MediaPipe, 24 -since there can be no recognition without previous detection). Note that all backends return somewhat different face regions (after their detection) -for example, MediaPipe seems to make a closer crop to the face- which may influence the recognition models to perform better or worse with certain backends (regardless of their detection capability).

Regarding models, DeepID is the fastest, followed by ArcFace and OpenFace, while ArcFace (216 recognitions) obtains the best performance, followed by VGG-Face (with 204 recognitions). OpenFace and DeepID, however, do not seem to work correctly with the hardware/libraries used (for M1), so they are disregarded going forward.

Notably also, even when building the model (build_model) prior to inference, the first iteration is by far the slowest -see Figure 3. This may not be a problem if multiple frames are processed without rebuilding the model, but it is important to keep in mind.

<div align="center">
  <img width="550" alt="Screenshot 2024-02-29 at 11 56 53" src="https://github.com/Any-Winter-4079/Transformer_Robot/assets/50542132/3d854e5a-fd70-4962-82c9-e6bd98d19794">
  <p>Figure 3. Face recognition time with Fast MTCNN as the backend and ArcFace as the model, in DeepFace. Notably, the first iteration is the slowest, although the proportional slowdown varies among backends (not shown in the figure).</p>
</div>

From this basis, it should be considered that in our use case, there is the possibility of encountering frames with unknown faces or without any faces in them. Therefore, the next step is to use [2_benchmark_face_recognition_with_unknown_and_no_faces](https://github.com/Any-Winter-4079/Transformer_Robot/blob/main/computer_code/face_recognition/2_benchmark_face_recognition_with_unknown_and_no_faces.py) to expand the type of possible images, thus working with a total of 48 images: 16 of unknown faces (from people not in the embeddings), 16 without faces (landscapes, etc.), and 16 faces of people present in the embeddings, from 4 identities (4 images per person) with shots in front/side and close/far combinations. Moreover, due to the predominance of frontal and close-up shots in the original dataset ('training'), it was decided to add 3 more images per person to be recognized, in poses of front from afar (1), side from afar (1), and side from close (1). In addition, all new images (both the 12 'training' images and the 48 testing images) are scaled to 250x250, to standardize them with the size of the LFW. The results obtained are shown in Figure 3.

<div align="center">
  <img width="700" alt="Screenshot 2024-02-29 at 12 06 16" src="https://github.com/Any-Winter-4079/Transformer_Robot/assets/50542132/6ad79030-61fc-4124-964a-6575d070e18e">
  <p>Figure 3. Number of identifications (out of 16) and non-identifications (out of 32) correct and average time per prediction for 4 models and 8 different backends in DeepFace, with cosine similarity and default thresholds.</p>
</div>

In Figure 4, one can observe the detail of recognitions by shots (with 4 images per shot), noting how frontal recognitions, whether close-up or far away, are the most frequent. This presents a greater difficulty in the case of side images, both close-up and especially from afar.

<div align="center">
  <img width="700" alt="Screenshot 2024-02-29 at 12 11 01" src="https://github.com/Any-Winter-4079/Transformer_Robot/assets/50542132/1618dd8b-9765-44ae-b79f-5134af7a038b">
  <p>Figure 4. Number of correct identifications (out of 4) for frontal/close, frontal/far, lateral/close, and lateral/far shots, for 4 models and 8 different backends in DeepFace, with cosine similarity and default thresholds.</p>
</div>

From the results, it is inferred that the default thresholds seem to induce certain undesired effects, with (depending on the backend-model combination) either a high tendency to discard almost all images (29/32 correct non-identifications with FaceNet512 and Fast MTCNN, for example, but only 5/16 correct identifications), or to assign a label to almost all images, with 10 to 12 -out of 16- correct identifications, but only 20/32 correct non-identifications, with VGG-Face and ArcFace, both with Fast MTCNN.

Experimenting with the recognition threshold (in Figure 5, from 0.68 to 0.625 for cosine similarity and VGG-Face) shows how it is possible to increase the correct non-identifications from 20 to 27/32, with only a slight loss of quality -from 12 to 11/16- in correct recognitions.

<div align="center">
  <img width="550" alt="Screenshot 2024-02-29 at 12 19 50" src="https://github.com/Any-Winter-4079/Transformer_Robot/assets/50542132/16bf64a1-3f1f-45f4-9c58-23e5186e3c15">
<p>Figure 5. Number of correct identifications (out of 16) and non-identifications (out of 32) and average time per prediction for 4 models and 8 different backends in DeepFace, with cosine similarity as the similarity metric and 0.625 as the recognition threshold.</p>
</div>

This behavior, if generalizable, is excellent for the robot, as if it manages to eliminate (or drastically reduce) the number of false detections (to avoid identifying unknown objects/people as known), even though the identification of faces suffers a slight decrease in performance, under the premise that a face is generally visible for a good number of frames, this small reduction in performance can be compensated with other techniques (such as combining the predictions from several images, along with the context of the LLM, to make an informed decision).

Additionally, in the test conducted, the embedding includes representations of 432 individuals, so a smaller number of people in the embedding could improve performance (for example, by reducing the probability of encountering two people with very similar faces). As the number of faces grows, however, the probability of success decreases (even for a human), and the need for the use of context (which in our case would come from the LLM) to assist in recognition becomes evident.

A higher resolution (as opposed to 250x250), quality, or number of images per person in the embedding, on the other hand, are also hypothesized to help, although this remains a hypothesis at this point.

The best course of action (having obtained the results from both experiments and formulated several hypotheses), nonetheless, seems to be the validation ([3_run_face_recognition](https://github.com/Any-Winter-4079/Transformer_Robot/blob/main/computer_code/face_recognition/3_run_face_recognition.py)) of these with real frames taken by the ESP32-CAM. For this purpose, a pair of masks/faces (of Tom Cruise and Jennifer Lawrence) are created, and the identification/non-identification of 3 faces (including my own) is tested, using a total of 13 images of Tom Cruise and 13 of my own, in 512x512, to create the embedding (not using images of Jennifer Lawrence, to carry out a non-recognition in her case and to be able to contrast both the recognition of known people and the non-recognition of unknown people). After the test, Fast MTCNN is verified as the best backend (under the conditions of this robot) for non-recognition and VGG-Face (with 0.625 as the threshold, as determined experimentally) as the best model, which under real conditions is tested to perform better than ArcFace. Given that Fast MTCNN is part of the group of the 4 fastest backends, and the speed of VGG-Face is reasonable (∼0.25s), it is considered feasible to work with them in real-time. Figure 6 shows some snapshots of the obtained results (marking the recognized faces with their bounding box and adding their name -taken from the ‘database’ on which the embedding is created- on them).

<div align="center">
  <img width="350" alt="Screenshot 2024-02-29 at 12 34 20" src="https://github.com/Any-Winter-4079/Transformer_Robot/assets/50542132/433211c3-87ee-454a-b0fa-125e34837637">
  <img width="350" alt="Screenshot 2024-02-29 at 12 34 33" src="https://github.com/Any-Winter-4079/Transformer_Robot/assets/50542132/e364b866-00dc-4e96-aca3-1d331e6662cc">
  <img width="350" alt="Screenshot 2024-02-29 at 12 35 30" src="https://github.com/Any-Winter-4079/Transformer_Robot/assets/50542132/0ae386f0-2b31-437c-a900-7633400cfb5c">
  <img width="350" alt="Screenshot 2024-02-29 at 12 35 43" src="https://github.com/Any-Winter-4079/Transformer_Robot/assets/50542132/c1be0ee1-546e-4abb-b058-f19b9dfba1b6">
  <img width="350" alt="Screenshot 2024-02-29 at 12 36 14" src="https://github.com/Any-Winter-4079/Transformer_Robot/assets/50542132/223843de-4c83-4afc-9c59-2caf2e470510">
  <img width="350" alt="Screenshot 2024-02-29 at 12 36 25" src="https://github.com/Any-Winter-4079/Transformer_Robot/assets/50542132/abae6b4d-2089-44aa-a2a5-9b39cb49550d">
  <p>Figure 6. Above, masks of Tom Cruise on the left, and Jennifer Lawrence on the right, used for validation. In the center, non-recognition (correct) of Jennifer Lawrence, for not being in the embeddings, on the left, and recognition (correct) of Tom Cruise, for being in the embeddings. Below, recognition (correct) of my face, for being in the embeddings, on the left, and a combination of previous scenarios, on the right.</p>
</div>



