// Server-side loader for Joyo review page
import { getJoyoKanji, getKanjiDetails, getJlptKanji } from '$lib/server/data';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async () => {
	// Build reverse lookup: character -> JLPT level
	const jlptData = getJlptKanji();
	const charToJlpt: Record<string, string> = {};
	for (const [level, chars] of Object.entries(jlptData)) {
		for (const char of chars) {
			charToJlpt[char] = level;
		}
	}
	
	return {
		joyoList: getJoyoKanji(),
		kanjiDetails: getKanjiDetails(),
		charToJlpt
	};
};

