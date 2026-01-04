// Server-side data loading and caching
// This module loads JSON data once and caches it in memory

// Type definitions
export interface CharNode {
	char: string;
	keyword?: string;
	meaning?: string;
	pinyin?: string;
	simp?: string;
}

export interface TreeNode {
	name: string;
	children?: (TreeNode | CharNode)[];
	color?: string;
}

export interface EquationData {
	char: string;
	gloss: string;
	components: { char: string; gloss: string }[];
	equation: string;
}

export interface KanjiDetail {
	kanji: string;
	strokes: number;
	jlpt: string;
	frequency: number;
	meaning: string;
	description: string;
}

// Cache for loaded data
let semanticGraph: TreeNode | null = null;
let charGlosses: Record<string, string> | null = null;
let equations: Record<string, EquationData> | null = null;
let componentGlosses: Record<string, string> | null = null;
let hskWords: Record<string, string[]> | null = null;
let jlptKanji: Record<string, string[]> | null = null;
let joyoKanji: string[] | null = null;
let kanjiDetails: Record<string, KanjiDetail> | null = null;

// Type for the fetch function passed from SvelteKit load functions
type FetchFn = typeof fetch;

async function loadJSON<T>(filename: string, fetchFn: FetchFn, origin: string): Promise<T> {
	const url = `${origin}/game_data/${filename}`;
	console.log(`📥 Fetching ${filename} from ${url}`);
	const response = await fetchFn(url);
	if (!response.ok) {
		throw new Error(`Failed to load ${filename}: ${response.status}`);
	}
	return response.json() as Promise<T>;
}

// Context type for data loading - passed from SvelteKit load functions
export interface DataLoadContext {
	fetch: FetchFn;
	origin: string;
}

// Async loaders with caching
export async function getSemanticGraph(ctx: DataLoadContext): Promise<TreeNode> {
	if (!semanticGraph) {
		semanticGraph = await loadJSON<TreeNode>('hanzi_semantic_graph.json', ctx.fetch, ctx.origin);
	}
	return semanticGraph;
}

export async function getCharGlosses(ctx: DataLoadContext): Promise<Record<string, string>> {
	if (!charGlosses) {
		charGlosses = await loadJSON<Record<string, string>>('char_glosses.json', ctx.fetch, ctx.origin);
	}
	return charGlosses;
}

export async function getEquations(ctx: DataLoadContext): Promise<Record<string, EquationData>> {
	if (!equations) {
		equations = await loadJSON<Record<string, EquationData>>('character_equations.json', ctx.fetch, ctx.origin);
	}
	return equations;
}

export async function getComponentGlosses(ctx: DataLoadContext): Promise<Record<string, string>> {
	if (!componentGlosses) {
		componentGlosses = await loadJSON<Record<string, string>>('component_glosses.json', ctx.fetch, ctx.origin);
	}
	return componentGlosses;
}

export async function getHskWords(ctx: DataLoadContext): Promise<Record<string, string[]>> {
	if (!hskWords) {
		hskWords = await loadJSON<Record<string, string[]>>('hsk_words.json', ctx.fetch, ctx.origin);
	}
	return hskWords;
}

export async function getJlptKanji(ctx: DataLoadContext): Promise<Record<string, string[]>> {
	if (!jlptKanji) {
		jlptKanji = await loadJSON<Record<string, string[]>>('jlpt_kanji.json', ctx.fetch, ctx.origin);
	}
	return jlptKanji;
}

export async function getJoyoKanji(ctx: DataLoadContext): Promise<string[]> {
	if (!joyoKanji) {
		joyoKanji = await loadJSON<string[]>('joyo_kanji.json', ctx.fetch, ctx.origin);
	}
	return joyoKanji;
}

export async function getKanjiDetails(ctx: DataLoadContext): Promise<Record<string, KanjiDetail>> {
	if (!kanjiDetails) {
		kanjiDetails = await loadJSON<Record<string, KanjiDetail>>('kanji_details.json', ctx.fetch, ctx.origin);
	}
	return kanjiDetails;
}

// Helper to check if a node is a character node
export function isCharNode(node: TreeNode | CharNode): node is CharNode {
	return 'char' in node;
}

// Build character to breadcrumb lookup
export function buildCharToBreadcrumb(node: TreeNode | CharNode, path: string[] = []): Record<string, string> {
	const result: Record<string, string> = {};
	
	if (isCharNode(node)) {
		result[node.char] = path.length > 0 ? path.join(' > ') : 'Not in semantic graph';
		return result;
	}
	
	const currentPath = node.name ? [...path, node.name] : path;
	
	if (node.children) {
		for (const child of node.children) {
			Object.assign(result, buildCharToBreadcrumb(child, currentPath));
		}
	}
	
	return result;
}

// Find a character in the graph
export function findCharInGraph(char: string, node: TreeNode | CharNode): CharNode | null {
	if (isCharNode(node)) {
		return node.char === char ? node : null;
	}
	
	if (node.children) {
		for (const child of node.children) {
			const found = findCharInGraph(char, child);
			if (found) return found;
		}
	}
	
	return null;
}

