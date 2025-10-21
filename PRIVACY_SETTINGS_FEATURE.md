# Privacy Settings Feature Documentation

## Overview

This feature allows applicants/job seekers to control what information recruiters can see on their profiles. Applicants can toggle visibility for various profile elements, ensuring they have full control over their privacy.

## User Story

**As an applicant/job seeker, I want to set privacy options on my profile so I control what recruiters can see.**

## Features Implemented

### 1. ProfilePrivacySettings Model

A new model that stores privacy preferences for each applicant with the following fields:

- **visible_to_recruiters**: Make profile visible in recruiter searches (default: True)
- **show_email**: Allow recruiters to see email address (default: True)
- **show_phone**: Allow recruiters to see phone number (default: True)
- **show_resume**: Allow recruiters to see resume link (default: True)
- **show_gpa**: Allow recruiters to see GPA in education records (default: True)
- **show_current_employment**: Allow recruiters to see current job status (default: True)
- **show_current_education**: Allow recruiters to see current education status (default: True)

### 2. Privacy Settings UI

Added a new "Privacy Settings" section to the applicant's profile view page (`/applicant/profile/view/`) with:

- Toggle switches for each privacy setting
- Real-time updates via AJAX (no page reload required)
- Clear labels and descriptions for each setting
- Visual feedback when settings are saved successfully

### 3. Privacy Enforcement

#### For Recruiter Searches

- Profiles with `visible_to_recruiters=False` are excluded from recruiter search results
- Applied in both the web UI (`/recruiter/candidate-search/`) and API (`/applicant/search/`)

#### For Protected Fields

When recruiters view candidate profiles:

- **Email**: Hidden if `show_email=False` (shows "[Hidden]" in API, contact buttons disabled in UI)
- **Phone**: Hidden if `show_phone=False` (shows "[Hidden]" in API)
- **Resume**: Hidden if `show_resume=False` (resume button disabled or shows "Resume (Hidden)")
- **GPA**: Removed from education records if `show_gpa=False`
- **Current Status Badges**: Hidden or marked as "Status Hidden" if respective settings are disabled

### 4. Backward Compatibility

- Privacy settings are created automatically when accessed (via `get_or_create_privacy_settings()`)
- Profiles without privacy settings default to all information visible (True)
- Template filter `get_privacy_setting` safely handles missing privacy settings

## Technical Implementation

### Models

- `ProfilePrivacySettings` in `applicant/models.py`
- One-to-one relationship with `Applicant` model
- Helper method `get_or_create_privacy_settings()` on Applicant model

### Views

- Updated `view_profile` in `applicant/views.py` to handle privacy settings updates
- Updated `candidate_search` in `recruiter/views.py` to filter by visibility
- Updated `applicant_search` in `applicant/views.py` to respect privacy settings in API

### Templates

- Enhanced `applicant/view_profile.html` with privacy settings section
- Updated `recruiter/candidate_search.html` to conditionally display protected information

### Template Tags

- Added `get_privacy_setting` filter in `applicant/templatetags/applicant_utils.py`
- Safely retrieves privacy settings with defaults

### Database

- Migration file: `applicant/migrations/0001_initial.py` includes ProfilePrivacySettings table

## Usage

### For Applicants

1. Navigate to "My Profile" (`/applicant/profile/view/`)
2. Scroll to the "Privacy Settings" section
3. Toggle any setting to enable/disable visibility
4. Settings are saved automatically
5. Look for the "Settings Saved" confirmation

### For Recruiters

- Only visible profiles appear in candidate searches
- Protected information is hidden or marked as unavailable
- Contact options are disabled when email/phone is hidden
- Clear indicators when information is hidden by candidate

## API Changes

### `/applicant/search/` Endpoint

Now filters results based on:

- User role (applicant vs recruiter)
- Privacy settings when accessed by recruiters
- Returns "[Hidden]" for protected fields
- Removes sensitive data based on privacy preferences

## Admin Panel

- New admin interface for `ProfilePrivacySettings`
- List view shows key privacy flags
- Searchable by applicant username/email
- Filterable by privacy settings

## Testing Recommendations

### Manual Testing

1. Create an applicant account
2. Go to profile view and toggle privacy settings
3. Create a recruiter account
4. Search for the applicant and verify protected information is hidden
5. Toggle `visible_to_recruiters` and verify profile disappears from search

### Unit Tests to Add

- Test privacy settings creation
- Test visibility filtering in candidate search
- Test field masking in API responses
- Test template rendering with different privacy settings
- Test backward compatibility with profiles without privacy settings

## Future Enhancements

- Granular control over which recruiters can see profile
- Privacy analytics (who viewed my profile)
- Temporary visibility options (e.g., visible for 30 days)
- Bulk privacy settings presets (e.g., "Maximum Privacy", "Fully Open")
- Privacy settings for individual work experiences or education entries
