"""Creative Professional Zettelkasten Templates - Photography, video, audio, and design notes."""

CREATIVE_TEMPLATES = {
    "photography": [
        {
            "title": "Photography Fundamentals",
            "folder": "creative/photography",
            "content": r"""# Photography Fundamentals

Photography is the art and science of capturing light to create images.

## The Exposure Triangle

```mermaid
graph TB
    A[Exposure Triangle]
    A --> B[Aperture<br/>Depth of Field]
    A --> C[Shutter Speed<br/>Motion]
    A --> D[ISO<br/>Sensitivity]
```

### Aperture (f-stop)
- [definition] Size of lens opening that lets light in
- [measurement] f/1.4, f/2.8, f/5.6, f/11, f/16
- [effect] Controls depth of field (background blur)

**Rules:**
- **Lower f-number** (f/1.4): Large aperture, shallow depth of field, blurry background
- **Higher f-number** (f/16): Small aperture, deep depth of field, sharp throughout

### Shutter Speed
- [definition] How long the sensor is exposed to light
- [measurement] 1/1000s, 1/250s, 1/60s, 1/15s, 1s
- [effect] Controls motion blur

**Rules:**
- **Fast shutter** (1/1000s): Freeze action
- **Slow shutter** (1/15s): Motion blur, light trails

### ISO
- [definition] Sensor sensitivity to light
- [measurement] 100, 200, 400, 800, 1600, 3200, 6400
- [effect] Controls image brightness and noise

**Rules:**
- **Low ISO** (100-400): Clean image, less noise, needs more light
- **High ISO** (1600+): Brighter in low light, more noise/grain

## Composition Rules

### Rule of Thirds
```
Grid:
 +---+---+---+
 | . | . | . |
 +---+---+---+
 | . | X | . |   X = Point of interest
 +---+---+---+
 | . | . | . |
 +---+---+---+
```

- [rule] Place subject at intersection points
- [benefit] More dynamic than center composition
- [application] Landscapes, portraits, any subject

### Leading Lines
- [technique] Use natural lines to guide eye to subject
- [examples] Roads, rivers, fences, buildings
- [benefit] Creates depth and draws attention

### Framing
- [technique] Use environmental elements to frame subject
- [examples] Doorways, windows, tree branches
- [benefit] Focuses attention and adds context

## Camera Modes

### Manual (M)
Full control over aperture, shutter, ISO.
- [use] When you need precise control
- [learning] Best mode to understand photography

### Aperture Priority (A/Av)
You set aperture, camera sets shutter speed.
- [use] Control depth of field
- [example] Portraits (shallow), landscapes (deep)

### Shutter Priority (S/Tv)
You set shutter speed, camera sets aperture.
- [use] Control motion
- [example] Sports (fast), waterfalls (slow)

### Auto (A+)
Camera controls everything.
- [use] Quick snapshots
- [limitation] Limited creative control

## Lighting Basics

### Natural Light
- **Golden Hour**: Hour after sunrise/before sunset (warm, soft)
- **Blue Hour**: Twilight (cool, moody)
- **Midday**: Harsh shadows (challenging)

### Direction of Light
- **Front Light**: Even, flat (least dramatic)
- **Side Light**: Texture and dimension
- **Back Light**: Silhouettes and rim light
- **Rembrandt Light**: 45° creates triangle under eye

## Relations
- enables [[Portrait Photography]]
- enables [[Landscape Photography]]
- related_to [[Image Editing]]
- uses [[Composition Techniques]]
- builds_on [[Visual Arts]]

## Practice Exercises

1. **Exposure Triangle**: Shoot same scene with different settings
2. **Rule of Thirds**: Compose 10 photos using the grid
3. **Lighting**: Same subject, different times of day
4. **Modes**: Compare manual vs auto mode results

*Photography is painting with light - master exposure and composition to tell visual stories.*
""",
        },
    ],
}
