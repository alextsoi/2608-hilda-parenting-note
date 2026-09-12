// @ts-check
import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';
import starlight from '@astrojs/starlight';

const site = process.env.SITE ?? 'https://hilda.lhl.hk';

// https://astro.build/config
export default defineConfig({
	site,
	integrations: [
		starlight({
			title: '2026 育兒筆記',
			defaultLocale: 'root',
			locales: {
				root: {
					label: '繁體中文',
					lang: 'zh-TW',
				},
			},
			sidebar: 			[
			  {
			    "label": "媽媽（產後）",
			    "items": [
			      {
			        "label": "概覽",
			        "slug": "mother"
			      },
			      {
			        "label": "休息同支援",
			        "slug": "mother/postnatal-needs"
			      },
			      {
			        "label": "情緒健康",
			        "slug": "mother/postnatal-mental-health"
			      },
			      {
			        "label": "伴侶／家人點照顧",
			        "slug": "mother/partner-support"
			      },
			      {
			        "label": "身體復元同避孕",
			        "slug": "mother/postnatal-care"
			      },
			      {
			        "label": "健康院產後服務",
			        "slug": "mother/services"
			      },
			      {
			        "label": "健康生活模式",
			        "slug": "mother/lifestyle"
			      },
			      {
			        "label": "哺乳營養",
			        "slug": "mother/breastfeeding-nutrition"
			      },
			      {
			        "label": "產後運動",
			        "slug": "mother/postnatal-exercise"
			      },
			      {
			        "label": "母乳（媽媽角度）",
			        "slug": "mother/breastfeeding"
			      }
			    ]
			  },
			  {
			    "label": "居家餐單",
			    "items": [
			      {
			        "label": "雙人月子餐",
			        "slug": "meal"
			      }
			    ]
			  },
			  {
			    "label": "初生至一個月",
			    "items": [
			      {
			        "label": "概覽",
			        "slug": "00-0-to-1-month"
			      },
			      {
			        "label": "親職／社交情緒",
			        "slug": "00-0-to-1-month/parenting"
			      },
			      {
			        "label": "母乳",
			        "slug": "00-0-to-1-month/breastfeeding"
			      },
			      {
			        "label": "奶瓶",
			        "slug": "00-0-to-1-month/bottle-feeding"
			      },
			      {
			        "label": "黃疸",
			        "slug": "00-0-to-1-month/jaundice"
			      },
			      {
			        "label": "臍帶",
			        "slug": "00-0-to-1-month/umbilical-cord"
			      },
			      {
			        "label": "求醫信號",
			        "slug": "00-0-to-1-month/health-warning-signs"
			      },
			      {
			        "label": "篩查",
			        "slug": "00-0-to-1-month/screening"
			      },
			      {
			        "label": "發展",
			        "slug": "00-0-to-1-month/development"
			      },
			      {
			        "label": "黑白對比圖案",
			        "slug": "00-0-to-1-month/high-contrast"
			      },
			      {
			        "label": "安全",
			        "slug": "00-0-to-1-month/safety"
			      },
			      {
			        "label": "口腔",
			        "slug": "00-0-to-1-month/oral"
			      },
			      {
			        "label": "疫苗",
			        "slug": "00-0-to-1-month/vaccines"
			      },
			      {
			        "label": "首次健康院",
			        "slug": "00-0-to-1-month/mchc-first-visit"
			      }
			    ]
			  },
			  {
			    "label": "一至十二個月",
			    "items": [
			      {
			        "label": "概覽",
			        "slug": "01-1-to-12-months"
			      },
			      {
			        "label": "親職",
			        "slug": "01-1-to-12-months/parenting"
			      },
			      {
			        "label": "奶類餵哺",
			        "slug": "01-1-to-12-months/feeding"
			      },
			      {
			        "label": "固體食物",
			        "slug": "01-1-to-12-months/feeding-solids"
			      },
			      {
			        "label": "發展",
			        "slug": "01-1-to-12-months/development"
			      },
			      {
			        "label": "聽力視力",
			        "slug": "01-1-to-12-months/hearing-vision"
			      },
			      {
			        "label": "疫苗",
			        "slug": "01-1-to-12-months/vaccines"
			      },
			      {
			        "label": "安全",
			        "slug": "01-1-to-12-months/safety"
			      },
			      {
			        "label": "口腔",
			        "slug": "01-1-to-12-months/oral"
			      }
			    ]
			  },
			  {
			    "label": "一歲至三歲",
			    "items": [
			      {
			        "label": "概覽",
			        "slug": "02-1-to-3-years"
			      },
			      {
			        "label": "親職",
			        "slug": "02-1-to-3-years/parenting"
			      },
			      {
			        "label": "奶類",
			        "slug": "02-1-to-3-years/feeding-milk"
			      },
			      {
			        "label": "發展",
			        "slug": "02-1-to-3-years/development"
			      },
			      {
			        "label": "視力",
			        "slug": "02-1-to-3-years/vision"
			      },
			      {
			        "label": "疫苗",
			        "slug": "02-1-to-3-years/vaccines"
			      },
			      {
			        "label": "安全",
			        "slug": "02-1-to-3-years/safety"
			      }
			    ]
			  },
			  {
			    "label": "三歲至六歲",
			    "items": [
			      {
			        "label": "概覽",
			        "slug": "03-3-to-6-years"
			      },
			      {
			        "label": "親職",
			        "slug": "03-3-to-6-years/parenting"
			      },
			      {
			        "label": "發展",
			        "slug": "03-3-to-6-years/development"
			      },
			      {
			        "label": "視力",
			        "slug": "03-3-to-6-years/vision"
			      },
			      {
			        "label": "營養",
			        "slug": "03-3-to-6-years/nutrition"
			      },
			      {
			        "label": "安全",
			        "slug": "03-3-to-6-years/safety"
			      },
			      {
			        "label": "口腔",
			        "slug": "03-3-to-6-years/oral"
			      }
			    ]
			  },
			  {
			    "label": "資源",
			    "items": [
			      {
			        "label": "概覽",
			        "slug": "resources"
			      },
			      {
			        "label": "小冊子總目",
			        "slug": "resources/happy-parenting"
			      },
			      {
			        "label": "（一）出生至一星期",
			        "slug": "resources/booklets/01"
			      },
			      {
			        "label": "（二）一星期至一個月",
			        "slug": "resources/booklets/02"
			      },
			      {
			        "label": "（三）一個月至兩歲",
			        "slug": "resources/booklets/03"
			      },
			      {
			        "label": "（四）兩歲至三歲",
			        "slug": "resources/booklets/04"
			      },
			      {
			        "label": "（五）三歲至六歲",
			        "slug": "resources/booklets/05"
			      },
			      {
			        "label": "完整疫苗表",
			        "slug": "resources/vaccination"
			      },
			      {
			        "label": "配方奶全文",
			        "slug": "resources/formula-advice"
			      },
			      {
			        "label": "健康院地址",
			        "slug": "resources/mchc-locations"
			      },
			      {
			        "label": "登記表格",
			        "slug": "resources/mchc-registration-form"
			      },
			      {
			        "label": "綜合計劃",
			        "slug": "resources/ichip"
			      },
			      {
			        "label": "講座",
			        "slug": "resources/public-talks"
			      },
			      {
			        "label": "網上學習",
			        "slug": "resources/parent-child-elearning"
			      },
			      {
			        "label": "育兒要訣",
			        "slug": "resources/parenting-tips"
			      },
			      {
			        "label": "小冊子（一）對照",
			        "slug": "resources/fhs-30032"
			      }
			    ]
			  }
			],
		}),
		sitemap(),
	],
});
