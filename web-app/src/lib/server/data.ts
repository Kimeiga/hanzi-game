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

// Base URL for fetching static files - works in both dev and production
function getBaseUrl(): string {
	// In production on Vercel, use the deployment URL
	if (process.env.VERCEL_URL) {
		return `https://${process.env.VERCEL_URL}`;
	}
	// In development, use localhost
	return 'http://localhost:5173';
}

async function loadJSON<T>(filename: string): Promise<T> {
	const url = `${getBaseUrl()}/game_data/${filename}`;
	console.log(`📥 Fetching ${filename} from ${url}`);
	const response = await fetch(url);
	if (!response.ok) {
		throw new Error(`Failed to load ${filename}: ${response.status}`);
	}
	return response.json() as Promise<T>;
}

// Async loaders with caching
export async function getSemanticGraph(): Promise<TreeNode> {
	if (!semanticGraph) {
		semanticGraph = await loadJSON<TreeNode>('hanzi_semantic_graph.json');
	}
	return semanticGraph;
}

export async function getCharGlosses(): Promise<Record<string, string>> {
	if (!charGlosses) {
		charGlosses = await loadJSON<Record<string, string>>('char_glosses.json');
	}
	return charGlosses;
}

export async function getEquations(): Promise<Record<string, EquationData>> {
	if (!equations) {
		equations = await loadJSON<Record<string, EquationData>>('character_equations.json');
	}
	return equations;
}

export async function getComponentGlosses(): Promise<Record<string, string>> {
	if (!componentGlosses) {
		componentGlosses = await loadJSON<Record<string, string>>('component_glosses.json');
	}
	return componentGlosses;
}

export async function getHskWords(): Promise<Record<string, string[]>> {
	if (!hskWords) {
		hskWords = await loadJSON<Record<string, string[]>>('hsk_words.json');
	}
	return hskWords;
}

export async function getJlptKanji(): Promise<Record<string, string[]>> {
	if (!jlptKanji) {
		jlptKanji = await loadJSON<Record<string, string[]>>('jlpt_kanji.json');
	}
	return jlptKanji;
}

export async function getJoyoKanji(): Promise<string[]> {
	if (!joyoKanji) {
		joyoKanji = await loadJSON<string[]>('joyo_kanji.json');
	}
	return joyoKanji;
}

export async function getKanjiDetails(): Promise<Record<string, KanjiDetail>> {
	if (!kanjiDetails) {
		kanjiDetails = await loadJSON<Record<string, KanjiDetail>>('kanji_details.json');
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

