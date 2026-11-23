# Art direction: the whole frame, not only the faces

Why this page exists: after twenty versions of faces, the creator still saw "a big gap" with the creators he
follows. The gap was never the face. Side by side with lucdgain's "LE SUPERMARCHÉ EP 01" (frames at 0:01, 0:14,
1:02), the difference was the whole frame: their characters stand in lit sets, ours floated on flat colour. Use
this page as the brief for every shot; it is checked against the reference in
`assets/comparaison_reference_vs_nous.jpg`.

## The brief (give it to yourself before drawing a shot)

> A vertical 1080x1920 frame of a night-job horror story. A real 3D set, dark, lit like cinema: one or two pools of
> cold light, deep black at the far end, a glossy floor that reflects the light. Our 2D characters stand IN it: a
> big-headed flat 2D figure with a thick outline, tinted by the set's light, a soft contact shadow under the feet.
> The camera is a person's: wide down the aisle, over the shoulder, or a close-up with the set blurred behind.
> One story object in the light (the thing that is wrong). A fixed HUD at the top. One caption line mid-screen in
> heavy white capitals with one orange word. Nothing else.

## Rules, with the reference that set each one

| Element | Rule | Seen in |
|---|---|---|
| Set | a real 3D set rendered in Blender (`scripts/supermarche.py`), not a flat painted colour | lucdgain (all frames), politiquepixels |
| Light | night: a few tubes on, some dead, one warm pool far away, exposure low, AgX medium-high contrast | lucdgain 0:14, 1:02 |
| Characters | full body about 3.2 heads tall (`scene5.figure5`), coloured top, tube arms with elbows, round hands, dark legs; close-ups use `toon5.bust5` | lucdgain, proteine.facile |
| Integration | tint each figure with the set's light (`place(..., tint)`), a blurred contact shadow, the far figure smaller and warmer if it stands in the warm pool | lucdgain 1:02 |
| Shots | wide down the aisle; over the shoulder (`scene5.back5`); close-up with the set blurred (depth by layers); the threat small and far, in the only light | lucdgain 0:01, 0:14, 1:02 |
| Story object | one object in the light that carries the anomaly (their giant teddy; ours: the till, the receipt, the phone) | lucdgain |
| HUD | top-left: an orange dot + the place in small heavy capitals, then "NUIT 1" in Anton with "/ 30"; top-right: a small orange label + an orange counter (our signature: the clock) | lucdgain ("JOUR 1 / 30", "SUR LE PARKING 300") |
| Captions | Inter Black, about 76 px, white with a dark stroke and a soft drop shadow, one keyword orange, centred mid-screen, 2-4 words | lucdgain, mission.creepy |
| Grade | cold, crushed blacks, a vignette (`scene5.vignette`) | all |
| Motion | on twos, `line_boil` per drawing, subtle moves, a long hold then a brutal pose | the Grease Pencil tutorials |
| Dark fantasy | violet in the shadows, a lavender moonlight line on the lit edge, the gold moon brooch, the double | our own theme |

## Commands

```bash
python3 -I scripts/supermarche.py s2/aisle.png aisle 24   # the set, about 2 min on CPU (cam: aisle | low)
python3 scripts/frames_s2.py                               # three test frames: wide, close, the double far away
```

Fonts: Anton (SIL OFL, from Google Fonts) for the HUD number; Inter Black (system) for captions and labels.

## Still behind the reference (say it, do not hide it)

- Their props are textured 3D models (the teddy); ours are boxes with flat colours. Next: one hero prop per episode
  (a Poly Haven model or a modelled till) in the light.
- Their sets have more mid-tones in the blue; ours fall to black faster. Raise the far tubes or the world light a
  little if a shot reads empty.
- Profile views and walking do not exist yet; use wide, over-the-shoulder and close-up until they do.
