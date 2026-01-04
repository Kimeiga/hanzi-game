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

	const categoryColors: Record<string, string> = {
		nature: '#22c55e',
		human: '#3b82f6',
		society: '#8b5cf6',
		objects: '#f59e0b',
		abstract: '#6366f1',
		communication: '#ec4899'
	};

	function isCharNode(node: TreeNode | CharNode): node is CharNode {
		return 'char' in node;
	}

	function countChars(node: TreeNode | CharNode): number {
		if (isCharNode(node)) return 1;
		return node.children?.reduce((sum, c) => sum + countChars(c), 0) ?? 0;
	}

	// Find category in the graph
	let categoryData = $derived.by(() => {
		const treeData = data.semanticGraph as TreeNode;
		if (!treeData?.children) return null;
		return treeData.children.find(
			(c): c is TreeNode => !isCharNode(c) && c.name.toLowerCase() === data.categoryName
		) || null;
	});

	let subcategories = $derived.by(() => {
		if (!categoryData?.children) return [];
		return categoryData.children.filter((c): c is TreeNode => !isCharNode(c));
	});

	let directChars = $derived.by(() => {
		if (!categoryData?.children) return [];
		return categoryData.children.filter((c): c is CharNode => isCharNode(c));
	});
</script>

<div class="explorer-container">
	<nav class="breadcrumb">
		<a href="/explorer">Hanzi Universe</a>
		<span class="separator">›</span>
		<span class="current">{categoryData?.name || data.categoryName}</span>
	</nav>

	{#if categoryData}
		<header class="category-header" style="--cat-color: {categoryColors[data.categoryName] || '#64748b'}">
			<h1>{categoryData.name}</h1>
			<p class="char-count">{countChars(categoryData)} characters</p>
		</header>

		{#if subcategories.length > 0}
			<section class="subcategories">
				<h2>Subcategories</h2>
				<div class="subcategory-grid">
					{#each subcategories as sub}
						<a href="/explorer/{data.categoryName}/{encodeURIComponent(sub.name.toLowerCase())}" class="subcategory-card">
							<span class="sub-name">{sub.name}</span>
							<span class="sub-count">{countChars(sub)} chars</span>
						</a>
					{/each}
				</div>
			</section>
		{/if}

		{#if directChars.length > 0}
			<section class="direct-chars">
				<h2>Characters</h2>
				<div class="char-grid">
					{#each directChars as char (char.char)}
						<a href="/character/{encodeURIComponent(char.char)}" class="char-card" title="{char.keyword}: {char.meaning || ''}">
							<span class="char">{char.char}</span>
							<span class="keyword">{char.keyword}</span>
						</a>
					{/each}
				</div>
			</section>
		{/if}
	{:else}
		<div class="error">Category "{data.categoryName}" not found</div>
	{/if}

	<a href="/explorer" class="back-link">← Back to Categories</a>
</div>

<style>
	.explorer-container { min-height: 100vh; background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #0f172a 100%); color: #e2e8f0; padding: 2rem; font-family: system-ui, -apple-system, sans-serif; }
	.breadcrumb { margin-bottom: 1.5rem; font-size: 0.875rem; }
	.breadcrumb a { color: #60a5fa; text-decoration: none; }
	.breadcrumb a:hover { text-decoration: underline; }
	.separator { color: #64748b; margin: 0 0.5rem; }
	.current { color: #94a3b8; }
	.category-header { margin-bottom: 2rem; }
	.category-header h1 { font-size: 2.5rem; font-weight: 700; color: var(--cat-color, #e2e8f0); margin-bottom: 0.25rem; }
	.char-count { color: #94a3b8; }
	h2 { font-size: 1.25rem; font-weight: 600; color: #94a3b8; margin-bottom: 1rem; }
	.subcategories, .direct-chars { margin-bottom: 2rem; }
	.subcategory-grid { display: flex; flex-wrap: wrap; gap: 1rem; }
	.subcategory-card { display: flex; flex-direction: column; padding: 1rem 1.5rem; background: #1e293b; border: 2px solid #334155; border-radius: 0.5rem; text-decoration: none; color: inherit; transition: all 0.2s; }
	.subcategory-card:hover { border-color: #60a5fa; background: #334155; }
	.sub-name { font-size: 1.125rem; font-weight: 600; color: #e2e8f0; }
	.sub-count { font-size: 0.75rem; color: #64748b; }
	.char-grid { display: flex; flex-wrap: wrap; gap: 0.75rem; padding-bottom: 5rem; }
	.char-card { display: flex; flex-direction: column; align-items: center; padding: 0.75rem; background: #1e293b; border: 1px solid #334155; border-radius: 0.5rem; min-width: 80px; cursor: pointer; transition: all 0.2s; text-decoration: none; color: inherit; }
	.char-card:hover { border-color: #60a5fa; background: #334155; transform: translateY(-2px); }
	.char { font-size: 2rem; line-height: 1; margin-bottom: 0.25rem; }
	.keyword { font-size: 0.625rem; color: #64748b; text-align: center; max-width: 70px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
	.loading, .error { text-align: center; padding: 4rem; }
	.error { color: #f87171; }
	.back-link { position: fixed; bottom: 2rem; left: 2rem; color: #60a5fa; text-decoration: none; font-weight: 600; padding: 0.75rem 1.5rem; background: #1e293b; border-radius: 0.5rem; border: 2px solid #334155; }
	.back-link:hover { background: #334155; border-color: #60a5fa; }
</style>
