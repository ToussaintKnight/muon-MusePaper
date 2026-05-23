const IMAGE_LIBRARY: Record<string, string[]> = {
  science: [
    '/engraving-science-01.jpg',
    '/engraving-science-02.jpg',
    '/hero-engraving-front.jpg',
  ],
  commerce: [
    '/engraving-commerce-01.jpg',
    '/engraving-commerce-02.jpg',
  ],
  arts: [
    '/engraving-arts-01.jpg',
    '/engraving-arts-02.jpg',
  ],
  society: [
    '/engraving-society-01.jpg',
    '/engraving-society-02.jpg',
  ],
  foreign: [
    '/engraving-foreign-01.jpg',
    '/engraving-foreign-02.jpg',
  ],
  front: [
    '/hero-engraving-front.jpg',
    '/engraving-domestic-01.jpg',
  ],
  classifieds: [
    '/ad-bovril.jpg',
    '/ad-pears-soap.jpg',
    '/ad-railway.jpg',
    '/ad-corsets.jpg',
    '/ad-tonic.jpg',
    '/ad-haberdashery.jpg',
  ],
  generic: ['/hero-engraving-front.jpg'],
};

function hashString(str: string): number {
  let hash = 0;
  for (let i = 0; i < str.length; i++) {
    const char = str.charCodeAt(i);
    hash = (hash << 5) - hash + char;
    hash = hash & hash;
  }
  return Math.abs(hash);
}

export function selectImage(theme: string, seed: string): string | undefined {
  const pool = IMAGE_LIBRARY[theme] || IMAGE_LIBRARY['generic'];
  if (!pool || pool.length === 0) return undefined;
  const index = hashString(seed) % pool.length;
  return pool[index];
}

export function placeImages<T extends { imageTheme: string; id: string; imageUrl?: string }>(
  items: T[]
): T[] {
  return items.map((item) => {
    if (item.imageUrl) return item;
    const imageUrl = selectImage(item.imageTheme, item.id);
    return { ...item, imageUrl };
  });
}
