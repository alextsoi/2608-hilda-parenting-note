import type { APIRoute } from 'astro';
import { getCollection } from 'astro:content';
import {
	docUrl,
	officialSources,
	siteDescription,
	siteTitle,
} from '../site';

export const GET: APIRoute = async ({ site }) => {
	if (!site) {
		return new Response('Site URL is not configured.', { status: 500 });
	}

	const docs = (await getCollection('docs')).sort((a, b) =>
		a.id.localeCompare(b.id, 'zh-HK'),
	);

	const keySlugs = [
		'index',
		'mother',
		'meal',
		'00-0-to-1-month',
		'01-1-to-12-months',
		'02-1-to-3-years',
		'03-3-to-6-years',
		'resources',
	];

	const byId = new Map(docs.map((entry) => [entry.id, entry]));
	const keyPages = keySlugs
		.map((id) => byId.get(id))
		.filter((entry) => entry !== undefined)
		.map((entry) => {
			const note = entry.data.description ? `: ${entry.data.description}` : '';
			return `- [${entry.data.title}](${docUrl(site, entry.id)})${note}`;
		});

	const allPages = docs.map((entry) => {
		const note = entry.data.description ? `: ${entry.data.description}` : '';
		return `- [${entry.data.title}](${docUrl(site, entry.id)})${note}`;
	});

	const officialLinks = officialSources.map(
		(source) => `- [${source.label}](${source.url})`,
	);

	const body = [
		`# ${siteTitle}`,
		'',
		`> ${siteDescription}`,
		'',
		'## 重點入口',
		'',
		...keyPages,
		'',
		'## 全部頁面',
		'',
		...allPages,
		'',
		'## 官方來源',
		'',
		...officialLinks,
		'',
	].join('\n');

	return new Response(body, {
		headers: { 'Content-Type': 'text/plain; charset=utf-8' },
	});
};
