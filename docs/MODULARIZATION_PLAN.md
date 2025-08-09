# API Modularization Plan - v2.2.0

## 🎯 **Objective**
Break down `api/main.py` (3,241 lines) into manageable modules of <500 lines each.

## 📊 **Current Structure Analysis**
- **33 routes** with `@app.route` decorators
- **33 functions** total
- **Major sections identified:**
  1. Field Normalization Middleware (lines 295-317)
  2. ChatGPT Hallucination Redirects (lines 317-463)
  3. Phase 2 Logging Endpoints (lines 463-591)
  4. Phase 2 Analysis Endpoints (lines 591-642)
  5. Phase 2 Location Endpoints (lines 642-739)
  6. Phase 2 Photo Upload Endpoints (lines 739-1104)
  7. Advanced Metadata Aggregation (lines 1104+)
  8. Core Functions (plant operations, log operations, etc.)

## 🏗️ **Target Module Structure**

### 1. **`api/core/__init__.py`** (~50 lines)
- Core imports and shared utilities
- App factory function

### 2. **`api/core/middleware.py`** (~100 lines)
- Field normalization middleware
- Authentication middleware
- Request preprocessing

### 3. **`api/routes/__init__.py`** (~50 lines)
- Route registration utilities
- Blueprint management

### 4. **`api/routes/plants.py`** (~400 lines)
- Plant management routes: add, search, get, update, remove
- Plant-specific utility functions
- Plant CRUD operations

### 5. **`api/routes/logs.py`** (~350 lines)
- Logging routes: create, search, create-for-plant
- Log management functions
- Upload token generation

### 6. **`api/routes/analysis.py`** (~300 lines)
- Plant analysis routes: diagnose, enhance-analysis
- Analysis utility functions
- AI integration helpers

### 7. **`api/routes/locations.py`** (~450 lines)
- Location context routes
- Container intelligence
- Garden metadata endpoints

### 8. **`api/routes/photos.py`** (~200 lines)
- Photo upload routes
- Token-based upload management
- Storage integration

### 9. **`api/routes/weather.py`** (~150 lines)
- Weather service routes (if any in main.py)
- Weather integration

### 10. **`api/core/functions.py`** (~400 lines)
- Core business logic functions
- Shared utilities
- Helper functions used across routes

### 11. **`api/main.py`** (~200 lines) - **SLIMMED DOWN**
- App initialization
- Route registration
- Configuration setup
- Entry point only

## 🔄 **Migration Strategy**

### Phase 1: Setup Module Structure
1. Create directory structure
2. Setup `__init__.py` files
3. Create blueprint framework

### Phase 2: Extract Route Groups
1. Extract plants routes → `routes/plants.py`
2. Extract logs routes → `routes/logs.py`
3. Extract analysis routes → `routes/analysis.py`
4. Extract location routes → `routes/locations.py`
5. Extract photo routes → `routes/photos.py`

### Phase 3: Extract Core Logic
1. Move middleware → `core/middleware.py`
2. Move shared functions → `core/functions.py`
3. Update imports across modules

### Phase 4: Integration & Testing
1. Update all imports
2. Register blueprints in main.py
3. Test all endpoints
4. Ensure <500 line limit per module

## ✅ **Success Criteria**
- [ ] All modules <500 lines
- [ ] All 33 routes working
- [ ] Clean import structure
- [ ] Maintained functionality
- [ ] Clear separation of concerns
- [ ] Easy to navigate and maintain

## 📈 **Expected Results**
- **Maintainability**: ⬆️ Much easier to find and modify specific functionality
- **Testing**: ⬆️ Isolated testing of specific modules
- **Collaboration**: ⬆️ Multiple developers can work on different modules
- **Code Quality**: ⬆️ Clear boundaries and responsibilities
- **Performance**: ➡️ No change (same logic, different organization)

