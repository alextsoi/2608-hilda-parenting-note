/** Starlight `head` entry for injecting third-party tags. */
export type HeadTag = {
	tag: string;
	attrs?: Record<string, string | boolean | undefined>;
	content?: string;
};

const GA4_ID_PATTERN = /^G-[A-Z0-9]+$/;

/** Production GA4 property for https://hilda.lhl.hk/ */
export const DEFAULT_GA_MEASUREMENT_ID = 'G-GKZ6EBTJB7';

/**
 * Build GA4 gtag.js tags for Starlight's `head` option.
 * Returns an empty array when the ID is missing or invalid (safe for local dev).
 */
export function getGa4Head(measurementId?: string): HeadTag[] {
	if (!measurementId || !GA4_ID_PATTERN.test(measurementId)) {
		return [];
	}

	const inlineScript = `
window.dataLayer = window.dataLayer || [];
function gtag(){dataLayer.push(arguments);}
gtag('js', new Date());
document.addEventListener('astro:page-load', () => {
  gtag('config', '${measurementId}', {
    page_path: window.location.pathname + window.location.search,
    page_title: document.title,
  });
});
`.trim();

	return [
		{
			tag: 'script',
			attrs: {
				async: true,
				src: `https://www.googletagmanager.com/gtag/js?id=${measurementId}`,
			},
		},
		{
			tag: 'script',
			content: inlineScript,
		},
	];
}
