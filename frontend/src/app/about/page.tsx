// frontend/src/app/about/page.tsx
import Image from 'next/image';

export default function AboutPage() {
  return (
    <div className="py-8 px-4">
      <h1 className="text-4xl font-bold text-pink-600 mb-8 text-center">About EverGlow</h1>

      <section className="mb-12 bg-white p-8 rounded-lg shadow-lg">
        <h2 className="text-3xl font-semibold text-gray-700 mb-4">Our Philosophy</h2>
        <p className="text-gray-600 leading-relaxed mb-4">
          At EverGlow, we believe that skincare should be a harmonious blend of nature and science.
          Our mission is to provide high-quality, 100% vegan skincare products that are kind to your skin and the planet.
          We are committed to using ethically sourced, plant-based ingredients that deliver visible results, helping you
          achieve a natural, radiant glow.
        </p>
        <p className="text-gray-600 leading-relaxed">
          We are passionate about transparency and sustainability. From our ingredient sourcing to our packaging,
          every decision is made with the utmost care for our customers and the environment. Join us on our journey
          to redefine beauty with products that are as pure and vibrant as nature itself.
        </p>
      </section>

      <section className="mb-12">
        <h2 className="text-3xl font-semibold text-gray-700 mb-6 text-center">Meet Our Team</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {/* Team Member 1 */}
          <div className="bg-white p-6 rounded-lg shadow-md text-center">
            <div className="relative w-[128px] h-[128px] mx-auto rounded-full overflow-hidden mb-4 border-2 border-pink-300">
              <Image src="https://picsum.photos/seed/picsum/200/300" alt="Team Member Jane Doe" fill style={{ objectFit: 'cover' }} />
            </div>
            <h3 className="text-xl font-semibold text-gray-800">Jane Doe</h3>
            <p className="text-pink-500">Founder & CEO</p>
            <p className="text-sm text-gray-500 mt-2">
              Jane is passionate about vegan living and sustainable beauty. She founded EverGlow to make a positive impact.
            </p>
          </div>

          {/* Team Member 2 */}
          <div className="bg-white p-6 rounded-lg shadow-md text-center">
            <div className="relative w-32 h-32 mx-auto rounded-full overflow-hidden mb-4 border-2 border-pink-300">
              <Image src="https://picsum.photos/seed/picsum/200/301" alt="Team Member John Smith" fill style={{ objectFit: 'cover' }} />
            </div>
            <h3 className="text-xl font-semibold text-gray-800">John Smith</h3>
            <p className="text-pink-500">Head of Product Development</p>
            <p className="text-sm text-gray-500 mt-2">
              John brings his expertise in botanical ingredients to create EverGlow&apos;s innovative formulas.
            </p>
          </div>

          {/* Team Member 3 */}
          <div className="bg-white p-6 rounded-lg shadow-md text-center">
            <div className="relative w-32 h-32 mx-auto rounded-full overflow-hidden mb-4 border-2 border-pink-300">
              <Image src="https://picsum.photos/seed/picsum/200/302" alt="Team Member Alice Green" fill style={{ objectFit: 'cover' }} />
            </div>
            <h3 className="text-xl font-semibold text-gray-800">Alice Green</h3>
            <p className="text-pink-500">Marketing Director</p>
            <p className="text-sm text-gray-500 mt-2">
              Alice spreads the word about EverGlow and connects with our wonderful community.
            </p>
          </div>
        </div>
      </section>

      <section className="bg-pink-50 p-8 rounded-lg shadow-md">
        <h2 className="text-3xl font-semibold text-gray-700 mb-4">Our Commitment</h2>
        <ul className="list-disc list-inside text-gray-600 space-y-2">
          <li><span className="font-semibold text-pink-500">100% Vegan:</span> All our products are free from animal-derived ingredients.</li>
          <li><span className="font-semibold text-pink-500">Cruelty-Free:</span> We never test on animals, and neither do our suppliers.</li>
          <li><span className="font-semibold text-pink-500">Sustainable Sourcing:</span> We prioritize ingredients that are ethically and sustainably sourced.</li>
          <li><span className="font-semibold text-pink-500">Eco-Friendly Packaging:</span> We strive to use recyclable and biodegradable materials.</li>
        </ul>
      </section>
    </div>
  );
}
