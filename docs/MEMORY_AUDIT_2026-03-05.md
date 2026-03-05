# Memory & Rules Audit - March 5, 2026

## Executive Summary

**Status:** ✅ **HIGH STANDARDS MAINTAINED**

The Sales Strategy Agent has comprehensive, well-organized rules maintaining data quality and user experience standards. Recent fixes addressed the critical table display issue.

---

## Files Audited

1. **CLAUDE.md** (main instructions) - 2,100+ lines
2. **MEMORY.md** (P0 checklist) - 34 critical rules
3. **leader-filtering.md** - Regional vs segment leader logic
4. **product-filtering.md** - Product-specific filters
5. **arr-formatting.md** - ARR display standards

---

## ✅ Strengths

### 1. **Comprehensive P0/P1/P2 Priority System**
- P0: Must do (always, no exceptions)
- P1: Should do (important for quality)
- P2: Nice to have (best practices)
- Clear prioritization helps agent focus on critical rules

### 2. **Clear Product Filtering Rules**
- AI Agents (specific): Ultimate, Ultimate_AR only
- AI products (broad): Ultimate, Ultimate_AR, Copilot
- Copilot (specific): Copilot only
- ES requires USE_CASE_C filter
- Well-documented decision tree

### 3. **Leader Filtering Logic**
- Regional leaders (AMER, EMEA, APAC, LATAM) exclude SMB/Digital
- Segment leaders (SMB, Digital) standalone
- NA → AMER conversion documented
- Standard ordering enforced

### 4. **Data Quality Standards**
- Required filters prevent duplicates
- NULL handling with COALESCE
- TOTAL row validation
- Fiscal calendar awareness (FY starts Feb)

### 5. **Output Standards**
- ARR formatting ($ sign, K/M rounding, highest-to-lowest bands)
- Table display thresholds (≤25 rows, <8 columns)
- Calculation accuracy (format only in final SELECT)
- CSV export workflow

---

## ⚠️ Areas to Monitor

### 1. **Rule Count: 34 Items in Checklist**
- **Status:** High but manageable
- **Risk:** Cognitive load on agent
- **Mitigation:** Rules are well-organized by topic
- **Action:** Monitor for rule fatigue

### 2. **Multiple Locations for Same Rule**
- CLAUDE.md (main instructions)
- MEMORY.md (checklist)
- **Risk:** Inconsistency if not synced
- **Mitigation:** Both files updated together
- **Action:** Continue updating both

### 3. **Command Template Visibility**
- **Fixed:** Now prominently at top of CLAUDE.md
- Visual emphasis with arrows
- WRONG vs CORRECT examples
- **Action:** Monitor if agent follows template

---

## 💡 Future Optimization Opportunities

### 1. **Group Rules by Workflow Stage**
```
Pre-Query:
- Check queries/ directory
- Identify required filters

Query Building:
- Apply filters
- Add ordering
- Include TOTAL row

Query Execution:
- Run with --format=table
- Cache results

Output:
- Show table
- Add insights
- Offer CSV
```

### 2. **Quick Reference Card**
Top 10 most critical rules on a single page

### 3. **More Visual Examples**
Add WRONG vs CORRECT examples throughout

### 4. **Testing Framework**
Automated tests for common queries

---

## 🚨 Critical Rules Status

### P0 Rules (10 Must-Check Items):

1. ✅ **--format=table command template** - AT TOP with visual emphasis
2. ✅ **Show table first, then insights** - Corrected per user feedback
3. ✅ **Required filters** - SERVICE_DATE, AS_OF_DATE, CRM_NET_ARR_USD
4. ✅ **Leader filtering** - Regional excludes SMB/Digital
5. ✅ **Standard ordering** - AMER→EMEA→APAC→LATAM→SMB→Digital
6. ✅ **Calculation accuracy** - Format only in final SELECT
7. ✅ **Opportunity lists** - Include ID + Total Booking
8. ✅ **No extra columns** - Only required + requested
9. ✅ **Product filtering** - AI Agents vs AI products distinction
10. ✅ **Output format** - ≤25 rows, <8 columns = show table

### Standards Maintained:

✅ Data quality filters enforced
✅ ARR formatting consistent
✅ Fiscal calendar documented (FY starts Feb)
✅ NA → AMER conversion rules
✅ Time comparison guidance (BCV vs non-BCV)
✅ Product-specific requirements (ES USE_CASE_C filter)
✅ Opportunity type analysis (New Business vs Expansion)
✅ Competitive analysis patterns (bot competitors)

---

## 🎯 Recent Fixes Applied

### Issue: Table Not Displaying
**Root causes identified:**
1. Missing `--format=table` flag on snow sql commands
2. "Be concise" misinterpreted as "skip table display"

**Fixes applied:**
1. ✅ Added prominent command template at top of CLAUDE.md
2. ✅ Clarified "be concise" means skip narration, NOT insights
3. ✅ Corrected to allow insights/summaries after table
4. ✅ Made --format=table #1 P0 rule
5. ✅ Added visual emphasis (arrows, REQUIRED labels)

---

## 📊 Metrics

- **Total P0 Rules:** 10 critical items
- **Total Checklist Items:** 34 rules
- **Memory Files:** 9 topic-specific files
- **Main Instruction File:** 2,100+ lines (CLAUDE.md)
- **Query Templates:** 15+ prebuilt queries
- **Version:** 1.2

---

## ✅ Recommendation

**Current State:** HIGH STANDARDS MAINTAINED

The rules are comprehensive, well-organized, and enforce data quality. The recent table display issue has been addressed with:

1. Prominent command template at top
2. Corrected "be concise" interpretation
3. Clear P0 prioritization
4. Visual emphasis on critical flag

**No major restructuring needed.**

---

## 📋 Next Steps

1. **Test agent** with new rules
   - Verify `--format=table` is used
   - Confirm table displays properly
   - Check that insights appear after table

2. **Monitor behavior** over next few queries
   - Watch for any rule regression
   - Track user feedback
   - Note any patterns of errors

3. **If issues persist**
   - May need additional blocking mechanism
   - Consider example-based learning
   - Evaluate if rule overload is factor

4. **Future enhancements**
   - Consider test environment setup (see TEST_ENVIRONMENT_GUIDE.md)
   - Add workflow-based grouping of rules
   - Create quick reference card

---

## 📁 Related Documents

- **CLAUDE.md** - Main instructions
- **MEMORY.md** - P0 checklist
- **TEST_ENVIRONMENT_GUIDE.md** - Test setup options
- **queries/** - Prebuilt query templates
- **.claude/memory/** - Topic-specific memory files

---

**Audit Date:** March 5, 2026
**Status:** ✅ HIGH STANDARDS MAINTAINED
**Action Required:** Monitor agent behavior with new fixes
