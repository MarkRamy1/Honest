from sqlalchemy.orm import Session
from app.core.security import get_password_hash
from app.models.user import User
from app.models.product import VerifiedProduct
from app.models.store import StoreReputation
from app.models.review import Review
from app.core.logging import logger


def seed_database(db: Session) -> None:
    """Seed initial verified products, trusted stores, reviews, and demo shopper account."""
    try:
        # 1. Create Default Honest Community User
        user = db.query(User).filter(User.email == "shopper@honestai.com").first()
        if not user:
            user = User(
                name="Honest Verified Buyer",
                email="shopper@honestai.com",
                hashed_password=get_password_hash("password123")
            )
            db.add(user)
            db.commit()
            db.refresh(user)

        # 2. Seed Verified Products
        product_count = db.query(VerifiedProduct).count()
        if product_count == 0:
            products = [
                VerifiedProduct(
                    name="Sony WH-1000XM5 Wireless Noise-Cancelling Headphones",
                    brand="Sony",
                    category="tech",
                    original_msrp=399.99,
                    high_copy_avg_price=58.00,
                    copy_avg_price=19.50,
                    authentic_materials="Custom carbon-fiber composite 30mm dome drivers, dual V1/QN1 DSPs, soft-fit synthetic leather headband with silent stepless slider, 8-mic array.",
                    fake_materials="Rigid ABS injection plastic, generic 40mm paper-cone drivers, unpadded cheap vinyl headband, single dummy microphone grill.",
                    verification_telltales=[
                        "Weight: Authentic is exactly 250g; fakes are usually 190-210g or over 285g with lead weights.",
                        "Hinges: Authentic swivel is dead-silent with calibrated friction; fakes have hollow snap clicks.",
                        "Sony Headphones Connect App: Copies and High-Copies CANNOT pair with Sony Connect App.",
                        "Microphone vents: Micro-perforated mesh with bronze trim on real units vs flat decal sticker."
                    ],
                    recommended_sources=[
                        {"tier": "original", "store": "Amazon Prime (Sony Store)", "price": 328.00, "url": "https://www.amazon.com/dp/B09XS7JWHH"},
                        {"tier": "high-copy", "store": "AliExpress Choice Plus 1:1 Batch", "price": 58.00, "url": "https://www.aliexpress.com/item/1005006283918234.html"},
                        {"tier": "copy", "store": "Temu Direct Sound", "price": 19.50, "url": "https://www.aliexpress.com/item/1005005829183921.html"}
                    ]
                ),
                VerifiedProduct(
                    name="Xiaomi Redmi 13 (6GB RAM, 128GB Storage, 108MP Camera, Midnight Black)",
                    brand="Xiaomi",
                    category="smartphones",
                    original_msrp=139.99,
                    high_copy_avg_price=89.00,
                    copy_avg_price=45.00,
                    authentic_materials="MediaTek Helio G91-Ultra 12nm SoC, 108MP Samsung ISOCELL sensor with 3x in-sensor zoom, 6.79-inch 90Hz FHD+ IPS LCD display with Corning Gorilla Glass, 5030mAh battery with 33W fast charging.",
                    fake_materials="Sluggish quad-core MediaTek MT6580 32-bit SoC, fake 108MP interpolated software camera (native 8MP sensor), 60Hz 720p TFT panel, generic 3000mAh battery with slow 10W charging.",
                    verification_telltales=[
                        "Check SoC via AIDA64: Authentic unit reports Helio G91-Ultra octa-core.",
                        "Camera: Real 108MP output creates ~25MB image files; clones output 2MB files.",
                        "Serial/IMEI: Traceable on mi.com/global/verify authentication portal."
                    ],
                    recommended_sources=[
                        {"tier": "original", "store": "Amazon Prime (Xiaomi Official Store)", "price": 139.99, "url": "https://www.amazon.com/dp/B0D5D8N5T9"}
                    ]
                ),
                VerifiedProduct(
                    name="Air Jordan 4 Retro Military Black",
                    brand="Nike Jordan",
                    category="sneakers",
                    original_msrp=210.00,
                    high_copy_avg_price=65.00,
                    copy_avg_price=26.00,
                    authentic_materials="Full-grain smooth white cowhide leather, soft micro-suede toe mudguard, polyurethane midsole with visible encapsulated heel Air unit, TPU lace cages.",
                    fake_materials="Low-density split leather with thick synthetic PU polyurethane coating (plastic feel), stiff cardboard-like netting, hollow rubber sole.",
                    verification_telltales=[
                        "Netting Angle: Side and tongue netting on authentic runs parallel to eyelet wings; budget fakes have horizontal netting.",
                        "Heel Tab: Back tab snaps back instantaneously when pressed down; budget fakes fold or slowly bounce back.",
                        "Jumpman Stitching: 4 fingers distinct on ball hand with crisp stitch borders; no loose connecting threads."
                    ],
                    recommended_sources=[
                        {"tier": "original", "store": "GOAT / StockX Verified Authentic", "price": 340.00, "url": "https://www.goat.com/sneakers/air-jordan-4-retro-military-black-dh6927-111"}
                    ]
                ),
                VerifiedProduct(
                    name="Rolex Submariner Date 126610LN",
                    brand="Rolex",
                    category="watches",
                    original_msrp=10250.00,
                    high_copy_avg_price=480.00,
                    copy_avg_price=45.00,
                    authentic_materials="Oystersteel (Grade 904L aerospace stainless steel), unidirectional 60-minute Cerachrom ceramic bezel with platinum-coated numerals, sapphire crystal with 2.5x Cyclops date magnifier.",
                    fake_materials="316L or cheap electroplated zinc alloy, painted aluminum bezel insert, mineral glass with blue-tinted 1.5x magnifier, cheap quartz or noisy 21j movement.",
                    verification_telltales=[
                        "Rehaut Engraving: Laser engraved ROLEX ROLEX ROLEX perfectly aligns with minute markers; serial at 6 o'clock.",
                        "Cerachrom Bezel: Real ceramic clicks crisp 120 times with zero back-play; platinum PVD filled numbers.",
                        "Crown Action: Real 3235 movement winds silky smooth without sandpaper resistance; instantaneous date jump at midnight."
                    ],
                    recommended_sources=[
                        {"tier": "original", "store": "Rolex Authorized Dealer / Chrono24 Certified", "price": 12500.00, "url": "https://www.chrono24.com/rolex/submariner-date--mod45.htm"}
                    ]
                ),
                VerifiedProduct(
                    name="Dyson Airwrap Multi-Styler Complete Long",
                    brand="Dyson",
                    category="tech",
                    original_msrp=599.99,
                    high_copy_avg_price=85.00,
                    copy_avg_price=32.00,
                    authentic_materials="High-velocity V9 digital motor spinning at 110,000 RPM, glass bead thermistor temperature regulation (under 150C), copper-anodized alloy barrels.",
                    fake_materials="Brushed DC motor (high noise, weak airflow under 30,000 RPM), basic nichrome heating wire with NO active thermal sensor (burns hair).",
                    verification_telltales=[
                        "Filter LED Indicator: Genuine Dyson flashes white/red when filter is clogged; fakes have static fake plastic LEDs.",
                        "Weight & Balance: Authentic wand weighs 660g with cold-touch barrel bases; fakes heat up quickly around the handle.",
                        "Magnetic filter cage: Genuine has fine laser-etched mesh that snaps cleanly; fakes use coarse plastic mesh."
                    ],
                    recommended_sources=[
                        {"tier": "original", "store": "Dyson Official / Amazon Prime Verified", "price": 549.00, "url": "https://www.amazon.com/dp/B0B68LTYJ6"}
                    ]
                ),

                VerifiedProduct(
                    name="Louis Vuitton Neverfull MM Damier Ebene",
                    brand="Louis Vuitton",
                    category="luxury",
                    original_msrp=2030.00,
                    high_copy_avg_price=140.00,
                    copy_avg_price=35.00,
                    authentic_materials="Treated waterproof coated canvas, natural untreated cowhide leather trim (Vachetta), solid brass hardware with deep crisp engraving, micro-striped textile lining.",
                    fake_materials="Thin printed PVC plastic with synthetic shine, stamped cardboard interior base, hollow brass-plated zinc alloy clips that tarnish within 2 months.",
                    verification_telltales=[
                        "Stitching: Exactly 5 stitches across the top of the handle tab in thick mustard-yellow beeswax thread.",
                        "Leather Trim: Genuine Vachetta leather darkens with sun and wear to a honey patina; plastic trim stays chalky white.",
                        "Date Code / RFID: Modern LV has embedded microchip or clean stamped heat code in font with perfect round 'O'."
                    ],
                    recommended_sources=[
                        {"tier": "original", "store": "Louis Vuitton Official / Fashionphile Certified Pre-Loved", "price": 1890.00, "url": "https://www.fashionphile.com/shop/louis-vuitton-neverfull-mm"},
                        {"tier": "high-copy", "store": "God Factory / OC Master Copy (1:1 Vachetta)", "price": 140.00, "url": "https://www.aliexpress.com/wholesale?SearchText=Neverfull+MM+God+Factory+1%3A1"},
                        {"tier": "copy", "store": "DHGate / Shein Monogram Tote", "price": 35.00, "url": "https://www.google.com/search?tbm=shop&q=checkerboard+tote+bag+neverfull"}
                    ]
                ),
                VerifiedProduct(
                    name="Fear of God Essentials Fleece Hoodie",
                    brand="Fear of God",
                    category="streetwear",
                    original_msrp=100.00,
                    high_copy_avg_price=32.00,
                    copy_avg_price=15.00,
                    authentic_materials="480 GSM Heavyweight 80% Cotton / 20% Polyester French terry/fleece, matte rubberized silicone heat-transfer chest logo, double-layered structured hood with rubber patch.",
                    fake_materials="240 GSM lightweight thin polyester fleece with high synthetic sheen, plastic shiny screenprint, floppy limp single-layer hood with crooked silicone label.",
                    verification_telltales=[
                        "Weight: Size L weighs over 850 grams on a digital scale; cheap copies weigh under 500g.",
                        "Silicone Hood Patch: Soft matte textured silicone; letters are perfectly centered and raised.",
                        "Neck Tag: Translucent silicone main tag sewn cleanly with black border stitching."
                    ],
                    recommended_sources=[
                        {"tier": "original", "store": "PacSun / SSENSE Official Stockist", "price": 100.00, "url": "https://www.ssense.com/en-us/men/designers/essentials"},
                        {"tier": "high-copy", "store": "Gman / Singor 1:1 Heavyweight Batch (AliExpress)", "price": 32.00, "url": "https://www.aliexpress.com/wholesale?SearchText=Essentials+Hoodie+heavyweight+Gman+1%3A1"},
                        {"tier": "copy", "store": "Shein Men Letter Graphic Drop Shoulder Hoodie", "price": 15.00, "url": "https://www.shein.com/search?keyword=essentials+oversized+hoodie"}
                    ]
                )
            ]
            for p in products:
                db.add(p)
            db.commit()

        # 3. Seed Stores Reputation
        store_count = db.query(StoreReputation).count()
        if store_count == 0:
            stores = [
                StoreReputation(
                    store_name="Amazon Prime Verified Brand Stores",
                    platform="Amazon",
                    specialty_tier="original",
                    trust_score=96,
                    material_honesty_rating=4.9,
                    verified_url="https://www.amazon.com",
                    notes="Direct fulfillment with strict serial verification and hassle-free returns."
                ),
                StoreReputation(
                    store_name="AliExpress Choice Plus (1:1 Verified Factories)",
                    platform="AliExpress",
                    specialty_tier="high-copy",
                    trust_score=91,
                    material_honesty_rating=4.7,
                    verified_url="https://www.aliexpress.com",
                    notes="Highest rated for 1:1 superclones (GX batch sneakers, VSF watches, God factory bags). 10-day guaranteed delivery."
                ),
                StoreReputation(
                    store_name="Shein Direct Fashion",
                    platform="Shein",
                    specialty_tier="copy",
                    trust_score=84,
                    material_honesty_rating=3.8,
                    verified_url="https://www.shein.com",
                    notes="Best for ultra-budget visual dupes. Fabric composition is usually polyblend or synthetic PU."
                ),
                StoreReputation(
                    store_name="Noon Express Verified",
                    platform="Noon",
                    specialty_tier="original",
                    trust_score=93,
                    material_honesty_rating=4.8,
                    verified_url="https://www.noon.com",
                    notes="Verified regional warehouse hub with fast 24h courier delivery and authenticity checks."
                )
            ]
            for s in stores:
                db.add(s)
            db.commit()

        # 4. Seed Reviews
        review_count = db.query(Review).count()
        if review_count == 0:
            reviews = [
                Review(
                    user_id=user.id,
                    user_name="Alex M. (Audio Engineer)",
                    product_name="Sony WH-1000XM5 Wireless Noise-Cancelling Headphones",
                    brand="Sony",
                    category="tech",
                    tier="original",
                    rating=5,
                    material_accuracy_rating=5,
                    price_paid=329.00,
                    store_purchased_from="Amazon Prime Verified",
                    product_url="https://www.amazon.com/dp/B09XS7JWHH",
                    comment="Genuine unit verified. ANC is whisper-quiet. The vegan leather headband is super soft and confirmed exactly 250g. Works flawlessly with Sony Connect app.",
                    is_verified_buyer=True,
                    upvotes=34
                ),
                Review(
                    user_id=None,
                    user_name="Tariq K. (Streetwear Curator)",
                    product_name="Air Jordan 4 Retro Military Black",
                    brand="Nike Jordan",
                    category="sneakers",
                    tier="high-copy",
                    rating=5,
                    material_accuracy_rating=4,
                    price_paid=65.00,
                    store_purchased_from="AliExpress GX Batch Store",
                    product_url="https://www.aliexpress.com",
                    comment="Insane 1:1 quality! The side netting angle is slanted correctly parallel to the wings, heel tab snaps back instantly, and the tumbled leather feels 90% as thick as my retail Jordan 4s. For $65 this saved me $275.",
                    is_verified_buyer=True,
                    upvotes=88
                ),
                Review(
                    user_id=None,
                    user_name="Marcus R. (Horology Enthusiast)",
                    product_name="Rolex Submariner Date 126610LN",
                    brand="Rolex",
                    category="watches",
                    tier="high-copy",
                    rating=5,
                    material_accuracy_rating=5,
                    price_paid=485.00,
                    store_purchased_from="VSF Superclone Dealer",
                    product_url="https://www.aliexpress.com",
                    comment="VSF 1:1 Superclone inspected under 10x loupe. Real 904L stainless steel, sapphire crystal with etched crown at 6 o'clock, ceramic bezel clicks 120 times crisply. Unless opened by a watchmaker, impossible to tell from retail.",
                    is_verified_buyer=True,
                    upvotes=112
                )
            ]
            for r in reviews:
                db.add(r)
            db.commit()

        logger.info("Database seeded successfully with initial verified products, stores, and reviews.")
    except Exception as e:
        logger.error(f"Error seeding database: {e}")
        db.rollback()
