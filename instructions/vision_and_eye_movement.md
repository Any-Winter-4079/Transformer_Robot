For the manufacture of the eyes, a Ping Pong ball (per eye) is used as a mold, filling it with Epoxy resin. In the center, it is important to note that either Blue Tack (or another similar material, but noting that it should not adhere to the Epoxy resin, to facilitate its removal) is used to create a space (when the resin is removed) through which to introduce the OV2640 through the eye, or drilling the resin once it has dried - which is not recommended - will be necessary. Similarly, if a piece of Ping Pong ball is cut and glued (to prevent the resin from exiting the main mold) inversely to the main ball, a concave area can be created on which to place the iris, and improve the appearance of the eye. Figure 10 shows one of these molds, already filled with Epoxy resin. Note that, depending on the level chosen to fill the main ball with resin, the eye will be more or less rounded at its back - that is, it can create from almost a hemisphere to almost a complete sphere.

<div align="center"><img width="500" alt="eye mold" src="https://github.com/Any-Winter-4079/Transformer_Robot/assets/50542132/b8dfaede-90ad-47bf-b804-17c341acc6f9">

  <p>Figure 10. Eye mold filled with Epoxy resin, with Blue Tack in the center to create space for the OV2640 and with part of a second ball placed inversely on the bottom, to generate a concave area on which to place the iris.
</p>
</div>

To paint the eyes, it is recommended to use white paint to cover the resin (transparent) and adhere several veins - created with thread - to it, joined with the paint itself, in this case white. After this, a gradient can be created, from red/pink to white, from the back to the front of the eye. Figure 11 shows the process of painting the eye and adhering veins to it, which are later (once the paint is dry) highlighted with red paint, potentially of different shades. Note how, in this case, the eye is a (nearly) hemisphere, whereas in the mold of Figure 10 (belonging to another attempt), the eye is (almost) a sphere.

<div align="center"><img width="500" alt="paint" src="https://github.com/Any-Winter-4079/Transformer_Robot/assets/50542132/996d41ff-6bf2-48a7-a021-faf8254d4317">

  <p>Figure 11. Process of painting and adhering veins to the eye.
</p>
</div>

Once the painting process is completed - and once dry - it is recommended to apply a thin layer of Epoxy resin to give a glossy appearance to the eye and, after that, the OV2640 can be introduced, filled with Blue Tack, and an iris - printed - placed on the front part. In Figure 12, two iterations of an eye design can be seen (spherical and hemispherical, and with more or less detail of veins). Ultimately, in this robot, the first manufactured eyes are used (see Figure 13), preferring a hemispherical design, only highlighting the veins on them a bit more. However, the more iterations are created, generally the better the result tends to be - see Figure 12.

<div align="center"><img height="200" alt="eye first it" src="https://github.com/Any-Winter-4079/Transformer_Robot/assets/50542132/19027293-ed83-4ac2-8197-0af26ac7fe35">
<img height="200" alt="eye second it" src="https://github.com/Any-Winter-4079/Transformer_Robot/assets/50542132/8533aab6-3cbd-468d-98e8-2c7b2d298564">
  <p>Figure 12. Result of the first iteration of eye manufacture (on the left) and second iteration, with OV2640 and Blue Tack inside it, (on the right).
</p>
</div>

<div align="center"><img width="500" alt="eye result" src="https://github.com/Any-Winter-4079/Transformer_Robot/assets/50542132/23f0cb46-9564-41ad-8479-98d3d2713dd6">
  <p>Figure 13. Final result of the eyes of the developed robot.</p>
</div>

Note that the space created for the iris could be filled with Epoxy resin to create a complete version of the (semi)sphere. However, cameras cannot see through the resin, so perhaps drilling through it might be the best alternative in that case. In such a scenario, painting the iris instead of printing it may be a better option, and in no case is it recommended to work with resin with the OV2640 installed. For a great eye design, with a bit more materials (such as a 3D printer), the animatronic eyes tutorial by [Will Cogley](https://youtube.com/watch?v=RqZRKUbA_p0) is recommended.

Once the eyes are manufactured, and for their movement, an additional platform is created (to be screwed to the upper face of the lower level), on which two wooden 'pillars' are glued at their ends (see Figure 14), which aim to hold a wooden cylinder (in this case, cut and sanded from the same block of wood) capable of rotation, as it will be pushed by an SG-90 servo to generate the (vertical) up and down movement of the eyes. See how the pillars thus have different heights, since one of them (in this case, the one closest to the robot's left eye) serves as support for an SG-90, while the other (taller) must have a hole at the height of the wooden cylinder, to allow its rotation through it. On the other hand, for horizontal movement from right to left, another SG-90 servo is fixed on the central part of the wooden cylinder, to which an arm is fixed (with one or several screws) that in turn is attached to a rear wooden slat that can transmit the right and left movement to two other wooden slats (one per eye) that are attached with Blue Tack to each eye. This mechanism, which uses 4 screws (2 to fix the wooden slats of the eyes to the wooden cylinder, and another 2 to join them to the rear slat) and 4 self-locking nuts, can be seen more clearly in Figure 14 itself.

Furthermore, it should be noted that, with this mechanism, the robot can move the eyes from right to left potentially at the same time as it raises or lowers the eyes - resulting in diagonal movements, if desired (see the [move_servos](https://github.com/Any-Winter-4079/Transformer_Robot/blob/main/arduino_uno_code/test_sketches/move_servos.ino) sketch) - since both movements do not interfere with each other.

<div align="center">
  <img height="500" alt="eye mech 1" src="https://github.com/Any-Winter-4079/Transformer_Robot/assets/50542132/8ef91f2c-5846-42e5-8a70-d6e5dc42c437">
  <img height="500" alt="eye mech 2" src="https://github.com/Any-Winter-4079/Transformer_Robot/assets/50542132/202b3b84-9674-4999-9820-6d1f0d3998d4">
<p>Figure 14. Eye mechanism, with emphasis on vertical movement guided by SG-90 servo placed on pillar close to the robot's left eye.</p>
</div>
