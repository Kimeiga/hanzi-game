// Server-side loader for HSK review page
import { getHskWords, type DataLoadContext } from '$lib/server/data';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ fetch, url }) => {
	const ctx: DataLoadContext = { fetch, origin: url.origin };
	return {
		hskData: await getHskWords(ctx)
	};
};

