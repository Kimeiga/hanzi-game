<script lang="ts">
	import type { PageData } from './$types';

	interface CharNode {
		char: string;
		simp: string | null;
		keyword: string;
		pinyin: string;
		meaning: string;
		study_order: number;
	}

	interface TreeNode {
		name: string;
		children?: (TreeNode | CharNode)[];
	}

	// Server-loaded data
	let { data } = $props<{ data: PageData }>();

	// Color scheme for top-level categories
	const categoryColors: Record<string, string> = {
		Nature: '#22c55e',
		Human: '#3b82f6',
		Society: '#8b5cf6',
		Objects: '#f59e0b',
		Abstract: '#6366f1',
		Communication: '#ec4899'
	};

	function isCharNode(node: TreeNode | CharNode): node is CharNode {
		return 'char' in node;
	}

	function countChars(node: TreeNode | CharNode): number {
		if (isCharNode(node)) return 1;
		return node.children?.reduce((sum, c) => sum + countChars(c), 0) ?? 0;
	}

	// Get the categories (children of root)
	let categories = $derived.by(() => {
		const treeData = data.semanticGraph as TreeNode;
		if (!treeData || !treeData.children) return [];
		return treeData.children.filter((c): c is TreeNode => !isCharNode(c));
	});

	// Get total character count
	let totalChars = $derived(countChars(data.semanticGraph as TreeNode));
</script>

<div class="explorer-container">
	<header class="explorer-header">
		<h1>🌌 Hanzi Universe</h1>
		<p class="subtitle">Explore {totalChars.toLocaleString()} Chinese Characters by Meaning</p>
		<p class="instructions">Click a category to explore its characters</p>
	</header>

	<nav class="category-grid">
		{#each categories as category}
			{@const charCount = countChars(category)}
			{@const color = categoryColors[category.name] || '#64748b'}
			<a
				href="/explorer/{encodeURIComponent(category.name.toLowerCase())}"
				class="category-card"
				style="--category-color: {color}"
			>
				<span class="category-name">{category.name}</span>
				<span class="category-count">{charCount} characters</span>
				{#if category.children}
					<span class="subcategory-list">
						{category.children
							.filter((c): c is TreeNode => !isCharNode(c))
							.map(c => c.name)
							.join(' · ')}
					</span>
				{/if}
			</a>
		{/each}
	</nav>

	<div class="nav-links">
		<a href="/explorer/hsk-review" class="review-link chinese">🇨🇳 HSK Review</a>
		<a href="/explorer/jlpt-review" class="review-link japanese">🇯🇵 JLPT Review</a>
		<a href="/explorer/joyo-review" class="review-link japanese">🇯🇵 Jōyō Kanji</a>
		<a href="/" class="back-link">← Back to Game</a>
	</div>
</div>

<style>
	.explorer-container {
		min-height: 100vh;
		background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #0f172a 100%);
		color: #e2e8f0;
		padding: 2rem;
		font-family: system-ui, -apple-system, sans-serif;
	}

	.explorer-header {
		text-align: center;
		margin-bottom: 2rem;
	}

	h1 {
		font-size: 2.5rem;
		font-weight: 700;
		margin-bottom: 0.5rem;
	}

	.subtitle {
		color: #94a3b8;
		font-size: 1.125rem;
		margin-bottom: 0.5rem;
	}

	.instructions {
		color: #64748b;
		font-size: 0.875rem;
		margin-bottom: 2rem;
	}

	.category-grid {
		display: grid;
		grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
		gap: 1.5rem;
		max-width: 1200px;
		margin: 0 auto;
		padding-bottom: 5rem;
	}

	.category-card {
		display: flex;
		flex-direction: column;
		padding: 1.5rem;
		background: #1e293b;
		border-radius: 0.75rem;
		border: 2px solid var(--category-color, #334155);
		text-decoration: none;
		color: inherit;
		transition: all 0.2s;
	}

	.category-card:hover {
		transform: translateY(-2px);
		box-shadow: 0 8px 30px rgba(0, 0, 0, 0.3);
		border-color: var(--category-color);
		background: #334155;
	}

	.category-name {
		font-size: 1.5rem;
		font-weight: 700;
		color: var(--category-color, #e2e8f0);
		margin-bottom: 0.5rem;
	}

	.category-count {
		font-size: 0.875rem;
		color: #94a3b8;
		margin-bottom: 0.75rem;
	}

	.subcategory-list {
		font-size: 0.8rem;
		color: #64748b;
		line-height: 1.4;
	}

	.loading, .error {
		text-align: center;
		font-size: 1.25rem;
		padding: 4rem;
	}

	.error {
		color: #f87171;
	}

	.nav-links {
		position: fixed;
		bottom: 2rem;
		left: 2rem;
		display: flex;
		gap: 1rem;
	}

	.back-link, .review-link {
		color: #60a5fa;
		text-decoration: none;
		font-weight: 600;
		padding: 0.75rem 1.5rem;
		background: #1e293b;
		border-radius: 0.5rem;
		border: 2px solid #334155;
		transition: all 0.2s;
	}

	.back-link:hover, .review-link:hover {
		background: #334155;
		border-color: #60a5fa;
	}

	.review-link {
		color: #fbbf24;
		border-color: #92400e;
	}

	.review-link:hover {
		border-color: #fbbf24;
	}

	.review-link.chinese {
		color: #fbbf24;
		border-color: #92400e;
	}

	.review-link.japanese {
		color: #f87171;
		border-color: #991b1b;
	}

	.review-link.japanese:hover {
		border-color: #f87171;
	}
</style>

