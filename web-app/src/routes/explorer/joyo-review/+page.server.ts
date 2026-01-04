// Server-side loader for Joyo review page
import { getJoyoKanji, getKanjiDetails, getJlptKanji, type DataLoadContext } from '$lib/server/data';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ fetch, url }) => {
	const ctx: DataLoadContext = { fetch, origin: url.origin };

	// Build reverse lookup: character -> JLPT level
	const jlptData = await getJlptKanji(ctx);
	const charToJlpt: Record<string, string> = {};
	for (const [level, chars] of Object.entries(jlptData)) {
		for (const char of chars) {
			charToJlpt[char] = level;
		}
	}

	return {
		joyoList: await getJoyoKanji(ctx),
		kanjiDetails: await getKanjiDetails(ctx),
		charToJlpt
	};
};

