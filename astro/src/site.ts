/** Shared site metadata for llms.txt and related endpoints. */
export const siteTitle = '2026 育兒筆記';
export const siteDescription =
	'整理、歸類同總結育嬰知識（繁體中文 · 香港）。內容係官方資料摘要，唔構成醫療建議。';

export const officialSources = [
	{
		label: '衞生署 · 兒童健康',
		url: 'https://www.fhs.gov.hk/tc_chi/health_info/child.html',
	},
	{
		label: '衞生署 · 婦女健康',
		url: 'https://www.fhs.gov.hk/tc_chi/health_info/class_topic/ct_woman_health/ct_woman_health.html',
	},
] as const;

export function docPath(id: string): string {
	return id === 'index' ? '/' : `/${id}/`;
}

export function docUrl(site: URL, id: string): string {
	return new URL(docPath(id), site).href;
}
