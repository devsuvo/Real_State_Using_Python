# Crystal Bay Estates — Real Estate Website (Django)

A responsive real estate website, with every piece of content editable from the Django admin.

## Run it

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_demo          # demo content + admin user (only on an empty database)
python manage.py runserver 127.0.0.1:8765
```

- Website:   http://127.0.0.1:8765/
- Dashboard: http://127.0.0.1:8765/dashboard/  (username `admin`, password `admin12345`; change it right away from the user menu → Change password)
- Django admin (advanced, superusers only): http://127.0.0.1:8765/admin/

To restore the demo content later, run `python manage.py seed_demo --reset`. This deletes everything you have edited.

## Dashboard

The custom dashboard at `/dashboard/` is the main place to manage the site:

- **Overview**: listing, lead, subscriber and post counts; a 30-day leads chart; portfolio value; recent leads; latest listings; quick links
- **Lists**: search, filters, sortable columns, on/off switches in the table (Featured, Published, Active…), bulk actions, pagination
- **Edit forms**: grouped sections, image upload or image link with live preview, color pickers, amenity chips, icon preview, a property photo-gallery manager, and a warning before you leave with unsaved changes
- **Inbox**: lead details (opening one marks it as read), reply by email, CSV export of leads and subscribers
- **Global search** across every content type, plus password change and logout
- Works on mobile, tablet and desktop. Only staff users can sign in.

To add a new section to the dashboard, add a `Resource(...)` entry in `dashboard/registry.py`.

## What you can edit

| Admin section | What it controls |
|---|---|
| **Site Settings** | Name, logo, favicon, brand colors, phone, email, address, social links, hero text, every home-page section's title, subtitle and on/off switch, CTA band, contact section, footer |
| **Hero Slides** | Background images of the home-page hero (they cross-fade automatically) |
| **Page Banners** | Title, subtitle and image for the Properties, Agents, About, Blog, Contact and Favorites pages |
| **About Page** | Intro text, images, years of experience, mission, vision and promise |
| **Why-Us Features / Stats / Pricing Plans / Testimonials** | The matching home-page sections |
| **Popups** | Popup title, text, image, form or button, delay, how often it shows, which pages it appears on |
| **Messages & Leads** | Every contact, property-inquiry, agent and popup submission |
| **Newsletter Subscribers** | Emails from the footer and blog sign-up forms |
| **Properties** | Listings with a photo gallery, amenities, price, details, video, featured/published switches |
| **Agents / Cities / Property Types / Labels / Amenities** | Supporting real estate data |
| **Blog Posts / Categories** | Articles. Start a line with `## ` to make it a heading |

**Images:** every image field accepts either an uploaded file or a pasted link (for example from Unsplash). An uploaded file takes priority over a link.

## Pages
Home · Properties (search, filters, sorting, grid/list view) · Property detail (gallery, map, inquiry form, similar properties) · Agents · Agent profile · About · Blog · Blog post · Contact · Saved properties (favorites) · 404

## Before going live
Set the environment variables `DJANGO_SECRET_KEY`, `DJANGO_DEBUG=0` and `DJANGO_ALLOWED_HOSTS=yourdomain.com`. Then run `python manage.py collectstatic` and serve `/media/` from your web server.
