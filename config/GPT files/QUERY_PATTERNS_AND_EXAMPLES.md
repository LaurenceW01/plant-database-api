# Query Pattern Recognition & Response Examples

**For GPT Reference: Recognize these patterns and respond with location-aware data**

## Pattern 1: Plant + Location Mentioned

### Input Patterns:
- "tropical hibiscus in the right arboretum"
- "how to water my roses in the patio"
- "fertilizer for azaleas by the pool"
- "care for my tomatoes in the rear middle bed"

### Required Response Pattern:
1. Find plant in database
2. Get specific location context
3. Provide integrated response with exact timing and container considerations

### Example Good Response:
```
🌺 Tropical Hibiscus Care - Right Arboretum

Current Setup:
- Location: arboretum right (Afternoon Sun pattern)
- Container: Medium plastic pot in ground
- Sun exposure: 6 hours (0 morning, 2 afternoon, 4 evening)
- Microclimate: North Facing (cooler temperatures)

Optimized Watering Plan:
- Best time: Very early morning (5:30-7:00 AM)
- Alternative: Early morning (7:00-8:30 AM)
- Avoid: Afternoon (2:00-6:00 PM), Evening (6:00-8:00 PM)
- Why: Your location gets 4 hours of evening sun, and plastic containers heat quickly

Container Considerations:
- Plastic material heats up fast in direct sun
- Early watering prepares plant for evening heat stress
- Check soil daily during hot weather

Weather Context: Given today's conditions [insert current weather], continue with early morning watering to prevent heat stress.
```

## Pattern 2: Plant Name Only (No Location)

### Input Patterns:
- "how to care for my hibiscus"
- "watering schedule for roses"
- "when to prune azaleas"

### Required Response Pattern:
1. Find all instances of plant in database
2. Get location context for each instance
3. Show care for ALL locations where plant exists

### Example Good Response:
```
🌺 Tropical Hibiscus Care - All Your Locations

I found your Tropical Hibiscus in 10 different locations! Here's the specific care for each:

**Right Arboretum** (6 hrs afternoon/evening sun)
- Container: Medium plastic pot
- Best watering: Very early morning (5:30-7:00 AM)
- Special note: Plastic heats quickly in evening sun

**Patio** (12 hrs full sun)  
- Container: Large ceramic pot
- Best watering: Very early morning (5:30-7:00 AM)
- Special note: Intense heat - daily watering checks needed

**Rear Left** (8 hrs dappled shade)
- Container: Medium plastic pot
- Best watering: Early morning (7:00-8:30 AM)
- Special note: Tree canopy protection reduces heat stress

[Continue for all 10 locations...]

Weather Impact: With today's forecast of [weather], focus extra attention on your full-sun locations (patio, pool path, rear middle).
```

## Pattern 3: Location-Specific Questions

### Input Patterns:
- "what's the best watering time for the right arboretum"
- "care strategy for plants in the patio"
- "how much sun does the rear middle get"

### Required Response Pattern:
1. Get location care profile
2. Show all plants in that location
3. Provide location-optimized care strategy

### Example Good Response:
```
🏡 Right Arboretum Care Strategy

Location Characteristics:
- Sun pattern: Afternoon Sun (6 total hours)
- Timing: 0 morning, 2 afternoon, 4 evening hours
- Microclimate: North Facing (cooler, less intense)
- Optimal watering: Very early morning (5:30-7:00 AM)

Plants in This Location:
- Tropical Hibiscus (Medium plastic pot)
- [Other plants if any]

Care Strategy:
- Water very early (5:30-7:00 AM) before evening heat
- Plastic containers need extra attention
- Cooler microclimate = less frequent watering than full sun spots
- Avoid afternoon/evening watering due to 4-hour evening sun exposure

Weather Considerations: [Current weather impact on this specific location]
```

## Pattern 4: Container-Specific Questions

### Input Patterns:
- "care for plants in plastic containers"
- "how often to water ceramic pots"
- "container material considerations"

### Required Response Pattern:
1. Find all containers of specified material
2. Group by location characteristics
3. Provide material + location integrated advice

## Anti-Patterns (What NOT to Do)

### ❌ Generic Response:
"Water hibiscus regularly, ensuring soil doesn't dry out. Use well-draining soil and fertilize monthly."

### ✅ Location-Aware Response:
"Your hibiscus in the right arboretum (medium plastic container, 6 hours afternoon sun) should be watered very early morning (5:30-7:00 AM) to prepare for evening heat stress. The north-facing microclimate keeps it cooler than your full-sun locations."

## Quick Reference Triggers

**ALWAYS call location endpoints when you see:**
- Plant names: hibiscus, rose, azalea, etc.
- Location words: arboretum, patio, rear, front, pool, kitchen, etc.
- Care words: water, fertilize, prune, care, schedule, etc.
- Container words: pot, container, plastic, ceramic, etc.
- Time words: when, how often, schedule, timing, etc.

**API Call Sequence for ANY Plant Care Query:**
1. `POST /api/plants/search` with `{"q": "{plant_name}"}` → Get ALL plants matching the name
2. `/api/plants/get-context/{id}` → Get location details for EACH found plant
3. `/api/weather/current` → Get current conditions
4. Integrate all three into specific, actionable response

**⚠️ CRITICAL**: For "where are all [plant]" or "find all [plant]" queries, you MUST use search first to find ALL matching plants (e.g., "Vinca" AND "Trailing Vinca"), then get context for each. Do NOT use get-context directly with a plant name as this only finds ONE specific plant.

**Character Count Optimization:**
- Lead with specific timing and location context
- Include container material considerations
- Reference microclimate impacts
- Always mention weather context
- Avoid generic plant care advice