"""
Fill the database with Crystal Bay Estates demo content.

    python manage.py seed_demo            # only seeds an empty database
    python manage.py seed_demo --reset    # wipes demo content and seeds again
"""
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from blog.models import Category, Post
from core.models import (
    AboutPage, ContactMessage, Feature, HeroSlide, PageHeader, Popup,
    PricingPlan, SiteSettings, Stat, Subscriber, Testimonial,
)
from properties.models import Agent, Amenity, City, Label, Property, PropertyImage, PropertyType


def U(photo_id):
    """Unsplash image URL; templates append the size parameters."""
    return f"https://images.unsplash.com/photo-{photo_id}?auto=format&fit=crop"


GALLERY_POOL = [
    "1600607687939-ce8a6c25118c", "1484154218962-a197022b5858", "1600566753086-00f18fb6b3ea",
    "1600210492486-724fe5c67fb0", "1586023492125-27b2c045efd7", "1554995207-c18c203602cb",
    "1600573472550-8090b5e0745e", "1560448204-e02f11c3d0e2", "1522708323590-d24dbb6b0267",
    "1502672260266-1c1ef2d93688", "1600566753190-17f0baa2a6c3",
]

AMENITIES = [
    ("Air Conditioning", "bi-snow"), ("Swimming Pool", "bi-water"), ("Fitness Center", "bi-heart-pulse"),
    ("Ocean View", "bi-binoculars"), ("Private Dock", "bi-life-preserver"), ("Smart Home System", "bi-phone"),
    ("Wine Cellar", "bi-cup-straw"), ("Home Theater", "bi-film"), ("Outdoor Kitchen", "bi-fire"),
    ("Laundry Room", "bi-basket"), ("High-Speed WiFi", "bi-wifi"), ("24/7 Security", "bi-shield-check"),
    ("Concierge", "bi-bell"), ("Covered Parking", "bi-car-front"), ("Private Balcony", "bi-columns-gap"),
    ("Landscaped Garden", "bi-flower1"), ("Pet Friendly", "bi-heart"), ("Impact Windows", "bi-wind"),
    ("Walk-in Closets", "bi-door-open"), ("Rooftop Terrace", "bi-brightness-high"),
]

PROPERTIES = [
    dict(
        title="Bayfront Modern Villa with Infinity Pool", city="Miami", type="Villa", status="sale", label="Hot Offer",
        agent="Isabella Moreno", price=4850000, address="4120 North Bay Road", zip="33140",
        beds=5, baths=5.5, garages=3, area=5200, lot=12500, year=2021, featured=True,
        img="1613490493576-7fde63acd811",
        excerpt="A glass-walled bayfront retreat with an infinity-edge pool, private dock and sunset views over Biscayne Bay.",
        desc="Set on a rare 12,500 sq ft bayfront lot, this architect-designed villa opens almost entirely to the water. Floor-to-ceiling glass slides away to join the great room with a travertine terrace and a 60-foot infinity pool that seems to spill straight into Biscayne Bay.\n\nInside, a chef's kitchen with Gaggenau appliances anchors the main level, while the primary suite occupies its own wing with a private terrace, spa bath and two dressing rooms. A 75-foot private dock, smart-home controls and impact glass throughout make it as practical as it is beautiful.",
        amenities=["Swimming Pool", "Ocean View", "Private Dock", "Smart Home System", "Wine Cellar", "Outdoor Kitchen", "Impact Windows", "Walk-in Closets"],
    ),
    dict(
        title="Brickell Sky Penthouse", city="Miami", type="Apartment", status="sale", label="New Listing",
        agent="Daniel Carter", price=2975000, address="1000 Brickell Plaza, PH 5101", zip="33131",
        beds=3, baths=3.5, garages=2, area=3100, lot=None, year=2019, featured=True,
        img="1560448204-e02f11c3d0e2",
        excerpt="A 51st-floor penthouse with wraparound terraces, private elevator entry and full-service resort amenities.",
        desc="Perched 51 floors above Brickell, this penthouse delivers uninterrupted views from the Atlantic to the Everglades. A private elevator opens into a gallery foyer and a sun-filled living space wrapped by more than 900 sq ft of terraces.\n\nResidents enjoy a two-level spa, rooftop pool deck, 24-hour concierge and valet, all within walking distance of Brickell City Centre's dining and shopping.",
        amenities=["Air Conditioning", "Ocean View", "Fitness Center", "Concierge", "24/7 Security", "Covered Parking", "Private Balcony", "Smart Home System"],
    ),
    dict(
        title="Las Olas Waterfront Family Home", city="Fort Lauderdale", type="Family Home", status="sale", label="Open House",
        agent="Sophia Nguyen", price=1695000, address="612 Isle of Palms Drive", zip="33301",
        beds=4, baths=3, garages=2, area=3450, lot=9800, year=2016, featured=True,
        img="1564013799919-ab600027ffc6",
        excerpt="Deep-water canal home minutes from Las Olas Boulevard, with a heated pool and 80 feet of dockage.",
        desc="Tucked along a quiet, deep-water canal just off Las Olas, this light-filled family home pairs coastal charm with everyday comfort. The open kitchen flows to a covered loggia, heated saltwater pool and 80 feet of dockage with no fixed bridges to the ocean.\n\nFour generous bedrooms, a dedicated home office and a fully fenced yard make it ideal for families, while boutiques and restaurants on Las Olas are a five-minute stroll away.",
        amenities=["Swimming Pool", "Private Dock", "Air Conditioning", "Landscaped Garden", "Pet Friendly", "Laundry Room", "Impact Windows"],
    ),
    dict(
        title="Coral Ridge Contemporary Residence", city="Fort Lauderdale", type="Villa", status="sale", label=None,
        agent="Daniel Carter", price=3250000, address="2800 NE 35th Street", zip="33306",
        beds=5, baths=4.5, garages=2, area=4600, lot=11000, year=2020, featured=True,
        img="1600585154340-be6161a56a0c",
        excerpt="Warm modernism among mature oaks — a two-storey glass-and-timber residence in prestigious Coral Ridge.",
        desc="Wrapped in mature oaks, this contemporary residence balances clean lines with warm timber and natural stone. Double-height glass fills the living areas with light, while a floating staircase leads to four upstairs suites and a family lounge.\n\nOutside, a covered summer kitchen and resort-style pool create a private oasis. Located in Coral Ridge, one of Fort Lauderdale's most established neighborhoods, near the beach and Galleria.",
        amenities=["Swimming Pool", "Outdoor Kitchen", "Smart Home System", "Home Theater", "Walk-in Closets", "Air Conditioning", "Covered Parking"],
    ),
    dict(
        title="Wynwood Industrial Loft", city="Miami", type="Loft", status="rent", label="Hot Offer",
        agent="Marcus Bennett", price=6800, suffix="/mo", address="250 NW 24th Street, Unit 4B", zip="33127",
        beds=2, baths=2, garages=1, area=1650, lot=None, year=2015, featured=True,
        img="1493809842364-78817add7ffb",
        excerpt="Soaring 14-foot ceilings, polished concrete and oversized windows in the heart of Miami's art district.",
        desc="Live among the murals in this authentic Wynwood loft. Fourteen-foot ceilings, polished concrete floors and factory-style windows give the space a gallery feel, while a modern kitchen and spa-inspired baths keep it effortlessly livable.\n\nThe building offers a rooftop terrace with skyline views, secure parking and a fitness studio. Galleries, coffee roasters and Miami's best restaurants are right outside your door.",
        amenities=["Air Conditioning", "Rooftop Terrace", "Fitness Center", "High-Speed WiFi", "Covered Parking", "Pet Friendly", "Laundry Room"],
    ),
    dict(
        title="Harbour Island Luxury Condo", city="Tampa", type="Apartment", status="rent", label=None,
        agent="Marcus Bennett", price=4200, suffix="/mo", address="700 S Harbour Island Blvd, #612", zip="33602",
        beds=2, baths=2, garages=1, area=1380, lot=None, year=2018, featured=True,
        img="1522708323590-d24dbb6b0267",
        excerpt="Water-view condo on exclusive Harbour Island, steps from the Riverwalk and downtown Tampa.",
        desc="Enjoy island living minutes from downtown in this bright two-bedroom condo overlooking the channel. An open-plan layout, quartz kitchen and private balcony make it perfect for both entertaining and quiet evenings.\n\nAmenities include a waterfront pool, fitness center, concierge and gated parking. Stroll to the Tampa Riverwalk, Amalie Arena and Sparkman Wharf.",
        amenities=["Air Conditioning", "Swimming Pool", "Fitness Center", "Concierge", "Private Balcony", "Covered Parking", "24/7 Security"],
    ),
    dict(
        title="Hyde Park Craftsman Family Home", city="Tampa", type="Family Home", status="sale", label="Best Deal",
        agent="Sophia Nguyen", price=985000, address="1712 W Swann Avenue", zip="33606",
        beds=4, baths=3, garages=2, area=2850, lot=7200, year=2008, featured=False,
        img="1583608205776-bfd35f0d9f83",
        excerpt="Classic wraparound porch, modern interiors and a shaded backyard on one of Hyde Park's prettiest streets.",
        desc="Rocking chairs on the wraparound porch, live oaks overhead — this Craftsman captures everything people love about Hyde Park. Inside, the home has been thoughtfully updated with wide-plank floors, a chef's kitchen and a first-floor guest suite.\n\nThe private backyard features a paver patio and lush landscaping. Walk to Hyde Park Village, Bayshore Boulevard and top-rated schools.",
        amenities=["Air Conditioning", "Landscaped Garden", "Pet Friendly", "Laundry Room", "Walk-in Closets", "Covered Parking"],
    ),
    dict(
        title="Sanibel Gulf-View Villa", city="Fort Myers", type="Villa", status="sale", label=None,
        agent="Isabella Moreno", price=2150000, address="3100 West Gulf Drive", zip="33957",
        beds=4, baths=4, garages=2, area=3900, lot=15000, year=2017, featured=True,
        img="1599809275671-b5942cabc7a2",
        excerpt="Mediterranean-style villa with spa pool and Gulf views, a short walk to Sanibel's famous shelling beaches.",
        desc="This Mediterranean-inspired villa brings resort living home. Arched loggias frame views toward the Gulf, and the pool deck with spa and fire feature is made for long golden-hour evenings.\n\nInside, coffered ceilings, a gourmet kitchen and four en-suite bedrooms offer space for family and guests. A private path leads to the beach, bike trails and the island's wildlife refuges.",
        amenities=["Swimming Pool", "Ocean View", "Outdoor Kitchen", "Impact Windows", "Air Conditioning", "Walk-in Closets", "Landscaped Garden"],
    ),
    dict(
        title="McGregor Boulevard Garden Home", city="Fort Myers", type="Family Home", status="sale", label="Best Deal",
        agent="Sophia Nguyen", price=749000, address="2245 McGregor Boulevard", zip="33901",
        beds=3, baths=2.5, garages=2, area=2300, lot=8600, year=2012, featured=False,
        img="1576941089067-2de3c901e126",
        excerpt="Charming garden home on palm-lined McGregor Boulevard, close to the river and historic downtown.",
        desc="On the city's iconic palm-lined boulevard, this charming home welcomes you with a manicured garden and covered front porch. The bright interior includes an open living and dining area, renovated kitchen and a sunroom overlooking the backyard.\n\nYou're minutes from the Caloosahatchee River, the Edison & Ford Winter Estates and the restaurants of the River District.",
        amenities=["Air Conditioning", "Landscaped Garden", "Pet Friendly", "Laundry Room", "Covered Parking"],
    ),
    dict(
        title="Tampa Riverwalk Loft", city="Tampa", type="Loft", status="rent", label="New Listing",
        agent="Marcus Bennett", price=3650, suffix="/mo", address="501 N Ashley Drive, Loft 9", zip="33602",
        beds=1, baths=1.5, garages=1, area=1100, lot=None, year=2019, featured=False,
        img="1600210492486-724fe5c67fb0",
        excerpt="Designer one-bedroom loft with river views, steps from the Riverwalk, museums and Curtis Hixon Park.",
        desc="A design-forward loft with a double-height living room, curated finishes and views over the Hillsborough River. The mezzanine bedroom offers privacy, while the main level opens up for entertaining.\n\nThe building includes a rooftop pool, co-working lounge and secure parking — all moments from the Riverwalk, museums and downtown offices.",
        amenities=["Air Conditioning", "Rooftop Terrace", "High-Speed WiFi", "Fitness Center", "Covered Parking", "Pet Friendly"],
    ),
    dict(
        title="Edgewater Bay-View Apartment", city="Miami", type="Apartment", status="rent", label="New Listing",
        agent="Daniel Carter", price=5400, suffix="/mo", address="600 NE 27th Street, #2207", zip="33137",
        beds=2, baths=2, garages=1, area=1450, lot=None, year=2022, featured=True,
        img="1502672260266-1c1ef2d93688",
        excerpt="Brand-new two-bedroom with sweeping bay views, between the Design District and Midtown.",
        desc="Wake up to Biscayne Bay from this brand-new 22nd-floor residence. Italian cabinetry, wide-plank floors and a deep balcony make the most of the views from every room.\n\nThe tower offers a bayfront pool, spa, co-working lounge and 24-hour concierge, with the Design District, Wynwood and Midtown all within minutes.",
        amenities=["Air Conditioning", "Ocean View", "Swimming Pool", "Fitness Center", "Concierge", "Private Balcony", "24/7 Security"],
    ),
    dict(
        title="Las Olas Penthouse Loft", city="Fort Lauderdale", type="Loft", status="sale", label=None,
        agent="Isabella Moreno", price=1125000, address="333 Las Olas Way, Loft 2801", zip="33301",
        beds=2, baths=2, garages=1, area=1800, lot=None, year=2018, featured=False,
        img="1600573472550-8090b5e0745e",
        excerpt="Two-storey glass loft with a floating staircase and a private terrace above the New River.",
        desc="This two-level loft is all about light and volume. A sculptural floating staircase connects an open entertaining level to a private bedroom floor, while a glass wall opens to a terrace overlooking the New River and the ocean beyond.\n\nResidents enjoy a resort pool, fitness center and valet, at the doorstep of Las Olas Boulevard.",
        amenities=["Air Conditioning", "Ocean View", "Rooftop Terrace", "Swimming Pool", "Concierge", "Smart Home System"],
    ),
    dict(
        title="Pinecrest Estate with Resort Pool", city="Miami", type="Family Home", status="sale", label="Open House",
        agent="Isabella Moreno", price=5600000, address="7400 SW 128th Street", zip="33156",
        beds=6, baths=6.5, garages=3, area=7400, lot=43560, year=2014, featured=True,
        img="1416331108676-a22ccb276e35",
        excerpt="A gated acre in Pinecrest with a Spanish-style main house, guest casita and resort-style pool.",
        desc="Behind private gates on a full acre, this Spanish-style estate is designed for multigenerational living and grand entertaining. The main house offers six suites, a library, a media room and a chef's kitchen with butler's pantry.\n\nThe grounds include a resort-style pool, outdoor kitchen, guest casita and lush tropical gardens — all within the acclaimed Pinecrest school district.",
        amenities=["Swimming Pool", "Outdoor Kitchen", "Home Theater", "Wine Cellar", "Landscaped Garden", "24/7 Security", "Walk-in Closets", "Impact Windows"],
    ),
    dict(
        title="Fort Myers Riverfront Villa", city="Fort Myers", type="Villa", status="rent", label=None,
        agent="Daniel Carter", price=9500, suffix="/mo", address="1450 River Edge Lane", zip="33919",
        beds=4, baths=4, garages=2, area=3600, lot=13000, year=2019, featured=False,
        img="1512917774080-9991f1c4c750",
        excerpt="Fully furnished riverfront villa with private pool and boat lift — available for seasonal or annual lease.",
        desc="Available fully furnished, this riverfront villa is perfect for a season in the sun or a year-round home. Wide sliding doors open the living areas to a private pool, summer kitchen and a dock with boat lift.\n\nEach of the four bedrooms has its own bath, and the home is a short drive to the beaches of Fort Myers and Sanibel.",
        amenities=["Swimming Pool", "Private Dock", "Outdoor Kitchen", "Air Conditioning", "High-Speed WiFi", "Impact Windows"],
    ),
]

AGENTS = [
    dict(name="Isabella Moreno", title="Founder & Principal Broker", photo="1573496359142-b8d87734a5a2",
         phone="(305) 555-0141", email="isabella@crystalbayestates.com", languages="English, Spanish",
         bio="Isabella founded Crystal Bay Estates after fifteen years advising luxury buyers across Miami-Dade. She has closed more than $900 million in waterfront sales and is known for discreet, off-market transactions.\n\nWhen she isn't negotiating, you'll find her paddleboarding on Biscayne Bay or supporting local arts organizations."),
    dict(name="Daniel Carter", title="Luxury Waterfront Specialist", photo="1560250097-0b93528c311a",
         phone="(305) 555-0156", email="daniel@crystalbayestates.com", languages="English, French",
         bio="A lifelong boater, Daniel understands dock depths, bridge clearances and sea-wall reports as well as he understands floor plans. He represents buyers and sellers of waterfront homes from Miami Beach to Fort Lauderdale.\n\nClients value his straightforward advice and meticulous preparation."),
    dict(name="Sophia Nguyen", title="Senior Buyer's Agent", photo="1544005313-94ddf0286df2",
         phone="(813) 555-0172", email="sophia@crystalbayestates.com", languages="English, Vietnamese",
         bio="Sophia helps families relocate to the Gulf Coast, specializing in Tampa and Fort Myers. She pairs neighborhood know-how with sharp market analysis so her clients buy with confidence.\n\nShe's a certified relocation professional and a mom of two who knows every great school and park in town."),
    dict(name="Marcus Bennett", title="Investment & Rentals Advisor", photo="1507003211169-0a1dd7228f2d",
         phone="(954) 555-0193", email="marcus@crystalbayestates.com", languages="English, Portuguese",
         bio="Marcus advises investors on rental yields, short-term rental regulations and 1031 exchanges. He also leads our leasing team, matching tenants with premium rentals across South Florida.\n\nBefore real estate, Marcus spent eight years in commercial banking."),
]

POSTS = [
    dict(title="South Florida Housing Market Outlook: What Buyers Should Know This Season", cat="Market Trends",
         img="1535498730771-e735b998cd64", author="Isabella Moreno", minutes=6,
         excerpt="Inventory is up, waterfront demand remains strong and buyers have more negotiating room than they've had in years. Here's what the numbers mean for you.",
         body="After several years of record-low inventory, South Florida's housing market is finding a healthier balance. Listings across Miami-Dade, Broward and the Gulf Coast have risen, giving buyers more choice and more time to decide.\n\n## Waterfront still leads the market\n\nDemand for direct-water homes remains remarkably resilient. Properties with ocean access, no fixed bridges and newer sea walls continue to attract multiple offers, while inland homes are seeing longer days on market.\n\n## More room to negotiate\n\nWith more inventory, buyers are successfully negotiating on inspection repairs, closing costs and, in some segments, price. Well-prepared buyers with pre-approval and a clear plan are in the strongest position.\n\n## Our advice\n\nFocus on long-term fit rather than timing the market perfectly. Work with an advisor who can show you true comparable sales, not just list prices — and be ready to move quickly when the right home appears."),
    dict(title="A First-Time Buyer's Guide to Waterfront Property in Florida", cat="Buying Guide",
         img="1560518883-ce09059eeffa", author="Daniel Carter", minutes=8,
         excerpt="Sea walls, flood zones, dock permits and insurance — the essential checklist before you buy your first home on the water.",
         body="Owning a home on the water is a dream for many buyers, but waterfront property comes with considerations you won't find inland.\n\n## Inspect the sea wall and dock\n\nA sea wall replacement can cost tens of thousands of dollars. Always order a specialist inspection and ask for permits on any past repairs.\n\n## Understand flood zones and elevation\n\nRequest the elevation certificate early. It affects insurance premiums, renovation options and long-term resale value.\n\n## Check water access\n\nIf boating matters to you, confirm water depth at low tide, the distance to open water and any fixed bridges along the route.\n\n## Budget for insurance\n\nGet insurance quotes during your inspection period, not after. Wind mitigation features like impact windows can significantly reduce premiums."),
    dict(title="Seven Staging Tips That Help Luxury Homes Sell Faster", cat="Selling Tips",
         img="1600566753086-00f18fb6b3ea", author="Isabella Moreno", minutes=5,
         excerpt="Small, intentional changes can add real value. Our listing team shares the staging moves that consistently attract premium offers.",
         body="Luxury buyers are buying a lifestyle, not just square footage. Staging helps them picture it.\n\n## 1. Edit ruthlessly\n\nRemove at least a third of the furniture and personal items. Space and light are the ultimate luxuries.\n\n## 2. Lead with the view\n\nArrange seating to face windows and water. Clean every pane of glass — it matters more than you'd think.\n\n## 3. Style the outdoor spaces\n\nIn Florida, terraces and pool decks are living rooms. Add quality lounge furniture, plants and soft lighting.\n\n## 4. Invest in professional photography\n\nMost buyers will see your home online first. Twilight photos and drone footage are worth every dollar."),
    dict(title="Miami vs. Fort Lauderdale: Choosing the Right Coastal City for You", cat="Lifestyle",
         img="1533106497176-45ae19e68ba2", author="Sophia Nguyen", minutes=7,
         excerpt="Both offer beaches, boating and sunshine — but the lifestyle, pace and price points are surprisingly different.",
         body="Only thirty miles apart, Miami and Fort Lauderdale each have a distinct personality.\n\n## Miami: global and energetic\n\nMiami offers world-class dining, art and nightlife, plus a booming financial district in Brickell. Expect high-rise living, international neighbors and premium prices in prime neighborhoods.\n\n## Fort Lauderdale: relaxed and boat-friendly\n\nWith more than 300 miles of navigable waterways, Fort Lauderdale is a boater's paradise. Neighborhoods feel calmer, and buyers often get more space for their money.\n\n## How to decide\n\nThink about your daily routine, commute and the kind of weekends you want. We're happy to arrange a day touring both cities so you can feel the difference yourself."),
    dict(title="How Today's Mortgage Rates Affect Your Buying Power", cat="Buying Guide",
         img="1560520653-9e0e4c89eb11", author="Marcus Bennett", minutes=5,
         excerpt="A one-point change in rates can shift your budget significantly. Here's how to plan, compare lenders and protect your rate.",
         body="Mortgage rates directly shape how much home your monthly budget can support.\n\n## Know your numbers\n\nGet fully pre-approved, not just pre-qualified. A lender who has reviewed your documents makes your offer far stronger.\n\n## Compare at least three lenders\n\nRates and fees vary more than most buyers expect. Ask for a Loan Estimate from each and compare them line by line.\n\n## Consider a rate lock\n\nOnce you're under contract, a rate lock protects you from increases before closing. Ask about float-down options too."),
    dict(title="Hurricane-Smart Homes: Features Florida Buyers Should Look For", cat="Buying Guide",
         img="1600047509807-ba8f99d2cdde", author="Daniel Carter", minutes=6,
         excerpt="Impact glass, roof straps and generator hookups don't just protect your home — they can lower insurance and boost resale value.",
         body="In Florida, a well-built home is a safer home and often a less expensive one to insure.\n\n## Impact windows and doors\n\nThey protect against wind-borne debris and eliminate the need for shutters, while also reducing noise and energy bills.\n\n## Roof age and construction\n\nInsurers look closely at roof age. Hip roofs with secondary water barriers and hurricane straps earn the best wind-mitigation credits.\n\n## Elevation and drainage\n\nCheck the finished floor elevation and how the lot drains. A higher home is a drier home.\n\n## Backup power\n\nA whole-home generator or battery system keeps essentials running after a storm."),
]


class Command(BaseCommand):
    help = "Seed the database with Crystal Bay Estates demo content."

    def add_arguments(self, parser):
        parser.add_argument("--reset", action="store_true", help="Delete existing demo content first.")

    @transaction.atomic
    def handle(self, *args, **opts):
        if opts["reset"]:
            for model in (PropertyImage, Property, Agent, City, PropertyType, Label, Amenity, Post, Category,
                          HeroSlide, PageHeader, Feature, Stat, PricingPlan, Testimonial, Popup,
                          ContactMessage, Subscriber):
                model.objects.all().delete()
            SiteSettings.objects.all().delete()
            AboutPage.objects.all().delete()
        elif Property.objects.exists():
            self.stdout.write(self.style.WARNING("Content already exists - use --reset to re-seed."))
            self._ensure_admin()
            return

        self._settings()
        self._pages()
        self._home_content()
        self._real_estate()
        self._blog()
        self._ensure_admin()
        self.stdout.write(self.style.SUCCESS("Crystal Bay Estates demo content created."))

    # ------------------------------------------------------------------
    def _ensure_admin(self):
        User = get_user_model()
        if not User.objects.filter(is_superuser=True).exists():
            User.objects.create_superuser("admin", "admin@crystalbayestates.com", "admin12345")
            self.stdout.write(self.style.SUCCESS("Superuser created - username: admin  password: admin12345"))

    def _settings(self):
        s = SiteSettings.load()
        s.meta_description = "Crystal Bay Estates is a South Florida luxury real estate brokerage helping clients buy, sell and rent waterfront homes, villas and condos in Miami, Fort Lauderdale, Tampa and Fort Myers."
        s.facebook = "https://www.facebook.com/"
        s.instagram = "https://www.instagram.com/"
        s.twitter = "https://x.com/"
        s.linkedin = "https://www.linkedin.com/"
        s.youtube = "https://www.youtube.com/"
        s.featured_subtitle = "Hand-picked homes our advisors would happily live in — from bayfront villas to sky-high penthouses."
        s.features_subtitle = "Two decades of local expertise, a hands-on team and the tools to make every move feel effortless."
        s.latest_subtitle = "Fresh to the market this week. Save the ones you love and we'll keep you posted."
        s.types_subtitle = "Whatever your pace of life, there's a corner of the Florida coast that fits it."
        s.cities_subtitle = "From Miami's skyline to the quiet beaches of the Gulf, explore the communities we know best."
        s.pricing_subtitle = "Owners and independent agents can showcase properties to thousands of qualified buyers every month."
        s.testimonials_subtitle = "Our reputation is built one client — and one closing — at a time."
        s.agents_subtitle = "Local specialists who answer the phone, know the streets and fight for your best outcome."
        s.blog_subtitle = "Practical advice and honest market analysis from our team of advisors."
        s.cta_text = "Find out what your home is worth in today's market. Our advisors prepare a detailed, no-obligation valuation within 48 hours."
        s.cta_image_url = U("1600585154340-be6161a56a0c")
        s.contact_subtitle = "Tell us what you're looking for and the right advisor will reply within one business day."
        s.contact_image_url = U("1600880292203-757bb62b4baf")
        s.footer_about = "Crystal Bay Estates is a boutique brokerage helping buyers, sellers and investors find exceptional homes across South Florida since 2005."
        s.copyright_text = "© 2026 Crystal Bay Estates. All rights reserved."
        s.save()

    def _pages(self):
        headers = [
            ("properties", "Find Your Next Home", "Browse villas, condos, lofts and family homes across South Florida.", "1564013799919-ab600027ffc6"),
            ("agents", "Meet Our Advisors", "Local experts who know every street, school and sea wall.", "1556761175-5973dc0f32e7"),
            ("about", "About Crystal Bay Estates", "A boutique brokerage built on trust, local knowledge and exceptional service.", "1613977257363-707ba9348227"),
            ("blog", "Market Insights & News", "Advice, analysis and inspiration for buyers, sellers and investors.", "1484154218962-a197022b5858"),
            ("contact", "Let's Talk", "We'd love to hear about your plans. Reach out and we'll be in touch within one business day.", "1600585154526-990dced4db0d"),
            ("favorites", "Your Saved Properties", "Homes you've shortlisted — compare them and book a viewing.", "1600210492486-724fe5c67fb0"),
        ]
        for page, title, sub, img in headers:
            PageHeader.objects.create(page=page, title=title, subtitle=sub, image_url=U(img))

        a = AboutPage.load()
        a.intro_text = ("Crystal Bay Estates began in 2005 with a simple belief: buying or selling a home should feel exciting, not exhausting. "
                        "Two decades later we're a team of 40 advisors across four offices, but we still run every transaction like a family business.\n\n"
                        "We combine deep local knowledge with modern marketing and data-driven pricing, so our clients make confident decisions — "
                        "whether that's a first condo in Tampa or a bayfront estate in Miami.")
        a.intro_image_url = U("1600880292203-757bb62b4baf")
        a.second_image_url = U("1600607687939-ce8a6c25118c")
        a.mission_text = "To guide every client through one of life's biggest decisions with honesty, expertise and genuine care."
        a.vision_text = "To be South Florida's most trusted name in real estate — recommended by clients to the people they love."
        a.values_text = "Clear communication, no pressure, and an advisor who answers the phone. Every single time."
        a.save()

    def _home_content(self):
        for i, img in enumerate(["1600596542815-ffad4c1539a9", "1613490493576-7fde63acd811", "1512917774080-9991f1c4c750", "1580587771525-78b9dba3b914"]):
            HeroSlide.objects.create(image_url=U(img), order=i, caption=f"Hero slide {i + 1}")

        features = [
            ("bi-search-heart", "Curated, Verified Listings", "Every home is personally previewed by an advisor, so the photos and details you see are accurate and up to date."),
            ("bi-graph-up-arrow", "Data-Driven Pricing", "We analyze true closed sales, not just asking prices, to help you buy smart and sell for the highest possible return."),
            ("bi-water", "Waterfront Specialists", "Dock depths, sea walls, bridge clearances and flood zones — we know the details that matter on the water."),
            ("bi-camera-video", "Private & Virtual Tours", "Tour homes in person or from anywhere in the world with live video walkthroughs led by your advisor."),
            ("bi-shield-check", "Expert Negotiation", "From offer to closing, we protect your interests and coordinate inspections, lenders and attorneys."),
            ("bi-translate", "Multilingual Team", "Our advisors speak English, Spanish, Portuguese, French and Vietnamese to serve international clients."),
        ]
        for i, (icon, title, desc) in enumerate(features):
            Feature.objects.create(icon=icon, title=title, description=desc, order=i)

        for i, (prefix, value, suffix, label) in enumerate([("", 1200, "+", "Homes Sold"), ("$", 2, "B+", "In Sales Volume"),
                                                           ("", 98, "%", "Client Satisfaction"), ("", 20, "+", "Years of Experience")]):
            Stat.objects.create(prefix=prefix, value=value, suffix=suffix, label=label, order=i)

        PricingPlan.objects.create(name="Starter", price=0, period="14 days", order=0,
                                   description="Try the platform with a single listing.",
                                   features="1 property listing\nUp to 10 photos\nListed for 14 days\nEmail support",
                                   button_text="Start Free")
        PricingPlan.objects.create(name="Professional", price=49, period="month", order=1, is_popular=True,
                                   description="For owners and agents with a growing portfolio.",
                                   features="10 property listings\n3 featured listings\nUnlimited photos & video\nPriority placement in search\nLead inbox & analytics",
                                   button_text="Choose Professional")
        PricingPlan.objects.create(name="Premier", price=129, period="month", order=2,
                                   description="Full-service marketing for luxury properties.",
                                   features="50 property listings\n15 featured listings\nProfessional photo & drone shoot\nDedicated marketing advisor\nSocial media campaign",
                                   button_text="Choose Premier")

        testimonials = [
            ("Jessica & Tom Harrington", "Bought a bayfront villa in Miami", "1494790108377-be9c29b29330",
             "Isabella found us a home that was never even listed publicly. Her team handled every detail of the inspection and closing while we were still living in Chicago. We couldn't have asked for a smoother move."),
            ("Rafael Ortiz", "Sold a family home in Fort Lauderdale", "1500648767791-00dcc994a43e",
             "Our house sold in nine days for above asking. The staging advice, photography and pricing strategy were spot-on, and Daniel kept us informed at every step."),
            ("Emily Carter", "First-time buyer in Tampa", "1438761681033-6461ffad8d80",
             "As a first-time buyer I had a hundred questions, and Sophia answered every one of them patiently. She helped me find a condo I love — under budget."),
            ("Richard Paulson", "Investor, 6 rental properties", "1472099645785-5658abf4ff4e",
             "Marcus understands the numbers better than anyone I've worked with. His rental projections were accurate to the dollar, and his leasing team keeps my units full."),
        ]
        for i, (name, role, photo, quote) in enumerate(testimonials):
            Testimonial.objects.create(name=name, role=role, photo_url=U(photo), quote=quote, order=i)

        Popup.objects.create(
            name="Off-market listings offer",
            eyebrow="Private Collection",
            title="Get Off-Market Listings Before Anyone Else",
            text="Nearly a third of our luxury sales never appear on public portals. Join our private list and receive hand-picked homes the moment they're available.",
            image_url=U("1600566753086-00f18fb6b3ea"),
            show_form=True,
            form_button_text="Send Me Private Listings",
            note="No spam, ever. Unsubscribe with one click.",
            delay_seconds=5,
            frequency="session",
            pages="all",
        )

    def _real_estate(self):
        cities = {}
        for i, (name, img) in enumerate([("Miami", "1506966953602-c20cc11f75e3"), ("Fort Lauderdale", "1507525428034-b723cf961d3e"),
                                         ("Tampa", "1535498730771-e735b998cd64"), ("Fort Myers", "1519046904884-53103b34b206")]):
            cities[name] = City.objects.create(name=name, image_url=U(img), order=i)

        types = {}
        for i, (name, icon, img) in enumerate([("Apartment", "bi-buildings", "1545324418-cc1a3fa10c00"),
                                               ("Family Home", "bi-house-heart", "1570129477492-45c003edd2be"),
                                               ("Loft", "bi-lamp", "1493809842364-78817add7ffb"),
                                               ("Villa", "bi-gem", "1613977257363-707ba9348227")]):
            types[name] = PropertyType.objects.create(name=name, icon=icon, image_url=U(img), order=i)

        labels = {}
        for name, color in [("Hot Offer", "#E5484D"), ("Open House", "#2F80ED"), ("New Listing", "#1F9D6B"), ("Best Deal", "#D9A44A")]:
            labels[name] = Label.objects.create(name=name, color=color)

        amenities = {name: Amenity.objects.create(name=name, icon=icon) for name, icon in AMENITIES}

        agents = {}
        for i, a in enumerate(AGENTS):
            agents[a["name"]] = Agent.objects.create(
                name=a["name"], title=a["title"], photo_url=U(a["photo"]), phone=a["phone"], email=a["email"],
                languages=a["languages"], bio=a["bio"], order=i,
                facebook="https://www.facebook.com/", instagram="https://www.instagram.com/", linkedin="https://www.linkedin.com/",
            )

        now = timezone.now()
        for i, d in enumerate(PROPERTIES):
            p = Property.objects.create(
                title=d["title"], status=d["status"], property_type=types[d["type"]], city=cities[d["city"]],
                label=labels.get(d["label"]), agent=agents[d["agent"]], price=d["price"], price_suffix=d.get("suffix", ""),
                address=d["address"], zip_code=d["zip"], bedrooms=d["beds"], bathrooms=d["baths"], garages=d["garages"],
                area=d["area"], lot_size=d["lot"], year_built=d["year"], excerpt=d["excerpt"], description=d["desc"],
                image_url=U(d["img"]), is_featured=d["featured"],
            )
            p.amenities.set([amenities[n] for n in d["amenities"]])
            pool = [g for g in GALLERY_POOL if g != d["img"]]
            for j in range(4):
                PropertyImage.objects.create(property=p, image_url=U(pool[(i * 3 + j) % len(pool)]), order=j)
            Property.objects.filter(pk=p.pk).update(created=now - timedelta(days=i * 2, hours=i * 5))

    def _blog(self):
        cats = {name: Category.objects.create(name=name) for name in ["Market Trends", "Buying Guide", "Selling Tips", "Lifestyle"]}
        agents = {a.name: a for a in Agent.objects.all()}
        now = timezone.now()
        for i, d in enumerate(POSTS):
            Post.objects.create(
                title=d["title"], category=cats[d["cat"]], author=agents.get(d["author"]), image_url=U(d["img"]),
                excerpt=d["excerpt"], body=d["body"], read_minutes=d["minutes"], published_at=now - timedelta(days=i * 6 + 1),
            )
