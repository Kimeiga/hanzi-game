// Server-side data loading and caching
// This module loads JSON data once and caches it in memory

import { readFileSync } from 'fs';
import { join } from 'path';

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

// Path to static data files
const DATA_DIR = join(process.cwd(), 'static', 'game_data');

function loadJSON<T>(filename: string): T {
	const filepath = join(DATA_DIR, filename);
	const content = readFileSync(filepath, 'utf-8');
	return JSON.parse(content) as T;
}

// Lazy loaders with caching
export function getSemanticGraph(): TreeNode {
	if (!semanticGraph) {
		console.log('📥 Loading semantic graph...');
		semanticGraph = loadJSON<TreeNode>('hanzi_semantic_graph.json');
	}
	return semanticGraph;
}

export function getCharGlosses(): Record<string, string> {
	if (!charGlosses) {
		console.log('📥 Loading char glosses...');
		charGlosses = loadJSON<Record<string, string>>('char_glosses.json');
	}
	return charGlosses;
}

export function getEquations(): Record<string, EquationData> {
	if (!equations) {
		console.log('📥 Loading equations...');
		equations = loadJSON<Record<string, EquationData>>('character_equations.json');
	}
	return equations;
}

export function getComponentGlosses(): Record<string, string> {
	if (!componentGlosses) {
		console.log('📥 Loading component glosses...');
		componentGlosses = loadJSON<Record<string, string>>('component_glosses.json');
	}
	return componentGlosses;
}

export function getHskWords(): Record<string, string[]> {
	if (!hskWords) {
		console.log('📥 Loading HSK words...');
		hskWords = loadJSON<Record<string, string[]>>('hsk_words.json');
	}
	return hskWords;
}

export function getJlptKanji(): Record<string, string[]> {
	if (!jlptKanji) {
		console.log('📥 Loading JLPT kanji...');
		jlptKanji = loadJSON<Record<string, string[]>>('jlpt_kanji.json');
	}
	return jlptKanji;
}

export function getJoyoKanji(): string[] {
	if (!joyoKanji) {
		console.log('📥 Loading Joyo kanji...');
		joyoKanji = loadJSON<string[]>('joyo_kanji.json');
	}
	return joyoKanji;
}

export function getKanjiDetails(): Record<string, KanjiDetail> {
	if (!kanjiDetails) {
		console.log('📥 Loading kanji details...');
		kanjiDetails = loadJSON<Record<string, KanjiDetail>>('kanji_details.json');
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

