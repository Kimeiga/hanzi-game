// Server-side loader for subsubcategory page
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ params }) => {
	return {
		categoryName: params.category,
		subcategoryName: params.subcategory,
		subsubcategoryName: params.subsubcategory
	};
};

