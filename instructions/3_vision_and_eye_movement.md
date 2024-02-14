For the creation of the eyes, a Ping Pong ball is used as a mold for each eye, filling it with Epoxy resin. It's important to highlight that either Blue Tack (or a similar material that does not adhere to the Epoxy resin, to facilitate its removal) is used to create a space (when the resin is removed) to insert the OV2640 through the eye, or one must drill into the resin once it's dry - which is not recommended. Similarly, if a piece of a Ping Pong ball is cut and glued (to prevent the resin from exiting the main mold) in reverse to the main ball, a concave area can be created on which to place the iris, enhancing the eye's appearance. Figure 1 shows one of these molds already filled with Epoxy resin. Note that the level to which the main ball is filled with resin determines how rounded the eye's back part will be - it can range from almost a semi-sphere to almost a complete sphere.

<div align="center"><img width="500" alt="eye mold" src="https://github.com/Any-Winter-4079/Transformer_Robot/assets/50542132/b8dfaede-90ad-47bf-b804-17c341acc6f9">

  <p>Figure 1. Eye mold filled with Epoxy resin, with Blue Tack in the center to create space for the OV2640 and with part of a second ball placed inversely on the bottom, to generate a concave area on which to place the iris.
</p>
</div>

For painting the eyes, it is recommended to use white paint to cover the resin (which is transparent) and attach several veins - created with thread - to it, bound together with the paint, in this case, white. After that, a gradient from red/pink to white can be created from the back to the front of the eye. Figure 2 shows the process of painting the eye and attaching veins to it, which are later emphasized with red paint, potentially in different shades, once the paint dries. Note how, in this case, the eye is a (nearly) semi-sphere, whereas in the mold of Figure 1 (belonging to another attempt), the eye is (almost) a sphere.

<div align="center"><img width="500" alt="paint" src="https://github.com/Any-Winter-4079/Transformer_Robot/assets/50542132/996d41ff-6bf2-48a7-a021-faf8254d4317">

  <p>Figure 2. Process of painting and adhering veins to the eye.
</p>
</div>

Once the painting process is finished - and once dry - it is recommended to apply a thin layer of Epoxy resin to give the eye a glossy appearance, and then the OV2640 can be introduced (importantly, in the same position in both eyes so that the frames from one camera are not rotated with respect to the other), fill the remaining space with Blue Tack, and place a printed iris - on the front part (in this case, created with DALL·E and available on the [resources](https://github.com/Any-Winter-4079/Transformer_Robot/blob/main/resources/iris.png) folder). Figure 3 shows two iterations of an eye design (spherical and semi-spherical, with more or less vein detail). Ultimately, in this robot, the first eyes made were used (see Figure 4), preferring a semi-spherical design, only emphasizing the veins a bit more. However, the more iterations created, generally the better the result - see Figure 3.

<div align="center"><img height="200" alt="eye first it" src="https://github.com/Any-Winter-4079/Transformer_Robot/assets/50542132/19027293-ed83-4ac2-8197-0af26ac7fe35">
<img height="200" alt="eye second it" src="https://github.com/Any-Winter-4079/Transformer_Robot/assets/50542132/8533aab6-3cbd-468d-98e8-2c7b2d298564">
  <p>Figure 3. Result of the first iteration of eye manufacture (on the left) and second iteration, with OV2640 and Blue Tack inside it, (on the right).
</p>
</div>

<div align="center"><img width="500" alt="eye result" src="https://github.com/Any-Winter-4079/Transformer_Robot/assets/50542132/23f0cb46-9564-41ad-8479-98d3d2713dd6">
  <p>Figure 4. Final result of the eyes of the developed robot.</p>
</div>

Note that the space created for the iris could be filled with Epoxy resin to create a complete version of the (semi)sphere. However, cameras cannot see through the resin, so perhaps drilling through it might be the best alternative in that case. In such a scenario, painting the iris instead of printing it may be a better option (to prevent the paper from getting wet with resin) , and in no case is it recommended to work with resin with the OV2640 installed. For a great eye design, with a bit more materials (such as a 3D printer), the animatronic eyes tutorial by [Will Cogley](https://youtube.com/watch?v=RqZRKUbA_p0) is recommended.

Once the eyes are made, and for their movement, an additional platform is created (to be screwed onto the upper face of the lower level), on which two wooden 'pillars' are glued (with Super Glue-3 or similar) at its ends (see Figure 5), which aim to hold a wooden cylinder (in this case, cut and sanded from the same block of wood) capable of rotating, as it will be pushed by an SG-90 servo to generate the (vertical) up and down movement of the eyes. Note how the pillars, therefore, have different heights, as one of them (in this case, the one closest to the robot's left eye) serves as support for an SG-90, while the other (taller) must have a hole at the height of the wooden cylinder, to allow its rotation through it. On the other hand, for the horizontal movement from right to left, another SG-90 servo is fixed on the central part of the wooden cylinder, to which an arm (with one or several screws) is attached that in turn is connected to a posterior wooden slat that can transmit the movement of right and left to two other wooden slats (one per eye) that are attached with Blue Tack to each eye. This mechanism, which uses 4 screws (2 to fix the wooden slats of the eyes to the wooden cylinder, and another 2 to join them to the posterior slat) and 4 self-locking nuts, can be seen more clearly in Figure 5 itself.

Additionally, it should be noted that, with this mechanism, the robot can move the eyes from right to left potentially at the same time as it raises or lowers the eyes - resulting in diagonal movements, if desired (see the [move_servos](https://github.com/Any-Winter-4079/Transformer_Robot/blob/main/arduino_uno_code/test_sketches/move_servos.ino) sketch) - since both movements do not interfere with each other.

<div align="center">
  <img height="500" alt="eye mech 1" src="https://github.com/Any-Winter-4079/Transformer_Robot/assets/50542132/8ef91f2c-5846-42e5-8a70-d6e5dc42c437">
  <img height="500" alt="eye mech 2" src="https://github.com/Any-Winter-4079/Transformer_Robot/assets/50542132/202b3b84-9674-4999-9820-6d1f0d3998d4">
<p>Figure 5. Eye mechanism, with emphasis on vertical movement guided by SG-90 servo placed on pillar close to the robot's left eye.</p>
</div>

By connecting the OV2640s to each ESP32-CAM (with the M5Stack Wide model for the right eye and Ai-Thinker for the robot's left eye, although they can be identical), we can proceed to writing the code to upload to the ESP32-CAMs. Here, some tips include checking the camera model to choose the correct pin layout (for example, D0 = 32 in M5Stack Wide, D0 = 5 in Ai-Thinker), playing with the clock frequency from 8MHz to 20MHz, the latter being faster but creating somewhat darker frames, using various networks to which the cameras can connect (for example, home router WiFi, mobile hotspot, etc.) to avoid having to reflash the code to the ESP32-CAMs if we find ourselves in an environment where the primary network is not available, making use of AsyncTCP, ESPAsyncWebServer, and esp32-camera, and experimenting with the position of the ESP32-CAM, trying to ensure its small antenna is not occluded/obstructed, among others. Additionally, it is recommended to set up a second endpoint on the camera server (in addition to /image.jpg which returns an image each time a GET call is made on it), for example, /camera_config, allowing the update (via POST call) of the camera settings - such as frame size or quality - from, for example, our computer without the need to reflash code to the camera.

The code [sketch](https://github.com/Any-Winter-4079/Transformer_Robot/blob/main/esp32_code/esp32-cam-aithinker.ino) for the Ai-Thinker model and the corresponding [sketch](https://github.com/Any-Winter-4079/Transformer_Robot/blob/main/esp32_code/esp32-cam_m5stackwide.ino) for M5Stack Wide with these functionalities can be sen on Github.
