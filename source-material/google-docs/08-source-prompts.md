<!-- Source: Prompts | https://docs.google.com/document/d/19kd4fB1CmY3CwyhQNuDpuyEDiSPioa-acMtCSSO2hMs/edit -->

1. LSA profile


> Please read @lsa-setup.md and create me a brief on my setup. Here's my website [link]




3. Build out Google Ads form


> Build out a next.js website with one page: a form. Make it look beautiful. The form should have 2 questions on it:
> - Out of 1-5 how likely would you be to refer us to your friends and family?
> - Do you have any feedback for our team?
> If the response is a 1-3, send data to this Make.com webhook (slack message)
> If it’s a 4-5, redirect user to leave a review on my google business profile here: [link]


3. Claude Code into Google Ads


> Read the @SETUP.md and walk me through connecting Google Ads.


4. Build the campaign


> Read the @campaign.md and build me a campaign for "plumber New York". Set it to PAUSED until I approve.


5. Build the ads


> Read the @ads.md and build me 3 RSAs for the plumber New York campaign. Add them into Google Ads and mark them as paused. Also read the @ad-assets.md and add the asset structure to my emergency plumber campaign.


6. Negative keywords




> Read the @negative-keywords-list.md and add the full universal negative keyword list to my account as a Shared Negative Keyword List, then attach it to my plumber New York campaign. Use BROAD match unless the term is in quotes or brackets.


7. Build the landing page


> Build a landing page for plumber New York in the Next.js site. Headline matches the keyword. Form + click-to-call. Hidden fields for gclid and UTMs. Use the attached screenshot for the design.


8. Tracking


> Add tracking to the landing page for both my phone number and form. I want to track the google ad click ID, the keyword and the campaign. For the form, send lead data to this URL [link], and for my phone, please set up click tracking code to send the data to this URL [link]. Send the tracking data above + any form/phone number info.




9. Add the conversion tracking + build a remarketing audience


> Read the @conversions.md and run it end-to-end. Create an audience for me to re-target.


10. Checking the conversion tracking is working


> Can you confirm that the conversion event fire on my website based on these tags that I'm copying in from the google tag assistant?


2. LSA Analytics


> I’m uploading two CSV files, one from my CRM tracking leads that closed, and one from my Google local ads dashboard. Please match leads based on the phone number, and tell me the % closing rate on: job type, location, lead type, time of day, and day of week I receive the leads.


11. Build an analytics dashboard


> Build me a dashboard at `/dashboard` in the Next.js site. Show ROAS from my LSA ads by job type, location, lead type, time of day, and day of week, and my search ads by campaign and keyword. Provide the top recommendations ranked by dollars recoverable.


12. Find search terms bleeding money and add them to negatives


> Read the @find-and-add-negatives.md and run it on my emergency plumber campaign. Show me the list with verdicts before adding anything.


13. Deploy the website to GitHub


> Push the website we built in this project to GitHub and connect Vercel. After deploy, confirm the conversion tag fires.


14. Skills


> Re-read the whole conversation and all the markdown files and please create a skills /build-campaign, /build-skags, /generate-ads, /build-landing-page, /audit-account, /clean-negatives

