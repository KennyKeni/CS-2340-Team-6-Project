# Quick Start Guide - Privacy Settings

## For Applicants/Job Seekers

### Setting Your Privacy Preferences

1. **Access Privacy Settings**

   - Log in to your account
   - Navigate to "My Profile" (usually in top navigation)
   - Scroll down to the "Privacy Settings" section

2. **Available Privacy Controls**

   | Setting                | What It Controls                                               |
   | ---------------------- | -------------------------------------------------------------- |
   | **Profile Visibility** | Makes your entire profile visible/hidden in recruiter searches |
   | **Email Address**      | Shows/hides your email from recruiters                         |
   | **Phone Number**       | Shows/hides your phone from recruiters                         |
   | **Resume**             | Shows/hides your resume link from recruiters                   |
   | **GPA**                | Shows/hides GPA in your education records                      |
   | **Current Job Status** | Shows/hides which job is your current position                 |
   | **Current Education**  | Shows/hides which education is in progress                     |

3. **How to Toggle Settings**

   - Simply click the toggle switch next to each setting
   - Green/ON = Visible to recruiters
   - Gray/OFF = Hidden from recruiters
   - Changes save automatically
   - Look for "Settings Saved" confirmation

4. **Example Scenarios**

   **Scenario 1: Passive Job Seeker**

   ```
   Profile Visibility: ON
   Email: OFF
   Phone: OFF
   Resume: OFF
   GPA: ON
   Current Job: OFF (don't want current employer to know you're looking)
   Current Education: ON
   ```

   **Scenario 2: Active Job Seeker**

   ```
   All settings: ON (fully open profile)
   ```

   **Scenario 3: Maximum Privacy**

   ```
   Profile Visibility: OFF (profile won't show in recruiter searches at all)
   All other settings: Doesn't matter if profile is hidden
   ```

## For Recruiters

### Understanding Privacy Settings

When searching for candidates, you may encounter:

1. **Hidden Profiles**

   - Won't appear in your search results at all
   - Candidate has set "Profile Visibility" to OFF

2. **Partial Information**

   - Profile visible but some fields hidden
   - You'll see indicators like:
     - "[Hidden]" in API responses
     - "Contact Hidden" or "Resume (Hidden)" buttons
     - "Status Hidden" badges

3. **What You Can Still See**

   - Name and username (always visible)
   - Skills (always visible)
   - Work experience and education (but not GPA/current status if hidden)
   - Projects/Links (always visible)
   - Location (always visible)

4. **How to Reach Hidden Contacts**
   - Use the platform's internal messaging system (if available)
   - Connect through professional networks
   - Respect candidate privacy preferences

## Technical Details

### Default Behavior

- **New users:** All settings default to ON (visible)
- **Existing users:** All settings default to ON until they change them
- **Missing settings:** Treated as visible (fail-safe)

### When Settings Apply

- **Recruiter searches:** Privacy settings are enforced
- **Recruiter profile views:** Privacy settings are enforced
- **API requests by recruiters:** Privacy settings are enforced
- **Other applicants:** Privacy settings are NOT enforced (applicants can see each other's full profiles)
- **Public/Guest users:** No access to profiles regardless of settings

### Data Security

- Settings are stored securely in the database
- Changes require authentication
- CSRF protection on all updates
- Privacy enforced at database query level (not just UI)

## Troubleshooting

### For Applicants

**Q: I toggled a setting but recruiters can still see my info**

- A: Make sure you see the "Settings Saved" confirmation
- Check your internet connection
- Try refreshing the page and checking the toggle state
- Clear browser cache if needed

**Q: Do privacy settings affect my job applications?**

- A: No! Once you apply to a job, the recruiter for that position can see your full profile

**Q: Can other applicants see my hidden information?**

- A: Currently, applicants can see each other's full profiles. Privacy settings only apply to recruiters.

### For Recruiters

**Q: Why can't I find a candidate I know exists?**

- A: They may have hidden their profile from recruiter searches

**Q: How can I contact a candidate with hidden contact info?**

- A: Use the platform's internal messaging if available, or look for their LinkedIn/other public profiles

**Q: Will hiding my recruiter status help me see more profiles?**

- A: No. Privacy settings are based on your account type, not your intentions.

## Best Practices

### For Applicants

✅ Review your privacy settings regularly
✅ Be strategic about what you hide (hiding everything may reduce opportunities)
✅ Update settings based on your job search status
✅ Consider keeping skills visible for better matching

### For Recruiters

✅ Respect candidate privacy preferences
✅ Use alternative channels if contact is hidden
✅ Focus on candidates who are open to being contacted
✅ Build your company's reputation to attract candidates

## Support

For issues or questions:

- Check the main documentation: `PRIVACY_SETTINGS_FEATURE.md`
- Review the implementation details: `IMPLEMENTATION_SUMMARY.md`
- Contact system administrators
- Report bugs through the issue tracker
