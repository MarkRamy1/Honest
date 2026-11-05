export const suggestions = [
  { icon: 'headphones', title: 'Find my next favorite', text: 'Find noise-cancelling headphones under $200' },
  { icon: 'shield', title: 'Look a little closer', text: 'How can I check if a product is authentic?' },
  { icon: 'scale', title: 'Make the right choice', text: 'Compare Sony WH-1000XM5 and Bose QuietComfort' },
  { icon: 'sparkles', title: 'Get more for my budget', text: 'Recommend a durable everyday backpack under $100' },
];
export const categories = ['All products', 'tech', 'sneakers', 'watches', 'luxury', 'streetwear'];
export const productPhotos: Record<string, string> = {
  tech: '/app/images/headphones.jpg', sneakers: '/app/images/sneakers.jpg',
  streetwear: '/app/images/jacket.jpg',
};
export const navigation = [
  { id: 'dashboard', label: 'Home Dashboard', icon: 'home' },
  { id: 'assistant', label: 'AI Assistant', icon: 'sparkles' },
  { id: 'analysis', label: 'Product Analysis', icon: 'scan' },
  { id: 'studio', label: 'Visual Reality Studio', icon: 'bag' },
  { id: 'compare', label: 'Comparison', icon: 'scale' },
  { id: 'extension', label: 'Chrome Extension', icon: 'download' },
  { id: 'saved', label: 'Saved products', icon: 'bookmark' },
  { id: 'reviews', label: 'Community', icon: 'users' },
] as const;

export const featuredProducts = [
  { name: 'Aura ANC Titanium Headphones', brand: 'Audio gear', category: 'tech', original_msrp: 349, image: '/app/images/aura-headphones.jpg', illustrative: true },
  { name: 'Arcana Precision Espresso Machine', brand: 'Kitchen hardware', category: 'Kitchen', original_msrp: 699, image: '/app/images/espresso.jpg', illustrative: true },
  { name: 'Aura Tower Air Purifier', brand: 'Climate care', category: 'Smart home', original_msrp: 220, image: '/app/images/air-purifier.jpg', illustrative: true },
  { name: 'ErgoCraft Studio 75 Keyboard', brand: 'Ergonomics', category: 'tech', original_msrp: 189, image: '/app/images/keyboard.jpg', illustrative: true },
];
export const popularScans = [{label:'Wireless Audio',query:'Sony WH-1000XM5 headphones'},{label:'Smart Home',query:'Smart air purifier'},{label:'Espresso Gear',query:'Breville Barista Express'},{label:'Mechanical Keyboards',query:'Mechanical keyboard'}];
export const features = [
  { title:'Analyze', icon:'scan', badge:'Product Scanner', description:'Look closer at materials, quality, and the claims behind the listing.', action:'Scan URL or Model', page:'analysis' },
  { title:'Compare', icon:'scale', badge:'Side by Side', description:'Explore buying options and compare value with a second opinion.', action:'Compare Options', page:'compare' },
  { title:'Visual Check', icon:'bag', badge:'Reality Studio', description:'Explore everyday lighting with a tailored image-generation prompt.', action:'Open Visual Studio', page:'studio' },
  { title:'Ask AI', icon:'sparkles', badge:'Honest Assistant', description:'Your conversational advisor for specs, budgets, and buying decisions.', action:'Start Consultation', page:'assistant' },
] as const;
