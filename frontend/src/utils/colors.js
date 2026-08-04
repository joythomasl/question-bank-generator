import brandIcons from './brandIcons.json'

// Deterministic color assignment for category tags and company badges.
// Known companies get a real brand-ish color; anything else (or a category,
// which has no "brand") is hashed onto a fixed vivid palette so the same
// name always lands on the same color without hand-maintaining a map that
// falls out of date as new categories/companies show up in scraped data.

const PALETTE = [
  '#7C9EFF', '#C084FC', '#2DD4BF', '#FB7185', '#22D3EE',
  '#FBBF24', '#A3E635', '#F472B6', '#818CF8', '#34D399',
  '#FB923C', '#60A5FA',
]

export function hashStringToColor(str) {
  let hash = 0
  for (let i = 0; i < str.length; i++) {
    hash = (hash << 5) - hash + str.charCodeAt(i)
    hash |= 0
  }
  return PALETTE[Math.abs(hash) % PALETTE.length]
}

export function getCategoryColor(category) {
  return hashStringToColor(category || 'General')
}

// Real interview-company brand colors (approximate, for the monogram badge
// background — not the actual logos, see CompanyLogo.jsx).
const COMPANY_BRAND_COLORS = {
  google: '#4285F4',
  amazon: '#FF9900',
  microsoft: '#00A4EF',
  meta: '#0866FF',
  facebook: '#0866FF',
  apple: '#A2AAAD',
  netflix: '#E50914',
  adobe: '#FF0000',
  oracle: '#F80000',
  uber: '#000000',
  bloomberg: '#000000',
  ibm: '#0F62FE',
  intel: '#0071C5',
  nvidia: '#76B900',
  salesforce: '#00A1E0',
  linkedin: '#0A66C2',
  twitter: '#1DA1F2',
  x: '#000000',
  airbnb: '#FF5A5F',
  spotify: '#1DB954',
  paypal: '#003087',
  goldman: '#7399C6',
  'goldman sachs': '#7399C6',
  jpmorgan: '#5A2D81',
  'jp morgan': '#5A2D81',
  flipkart: '#2874F0',
  atlassian: '#0052CC',
  vmware: '#607078',
  cisco: '#1BA0D7',
  samsung: '#1428A0',
  qualcomm: '#3253DC',
  amd: '#ED1C24',
  sap: '#0FAAFF',
  visa: '#1A1F71',
  mastercard: '#EB001B',
  twilio: '#F22F46',
  shopify: '#95BF47',
  stripe: '#635BFF',
  dropbox: '#0061FF',
  yahoo: '#6001D2',
  ebay: '#E53238',
  zoom: '#2D8CFF',
}

export function getCompanyColor(company) {
  const key = (company || '').trim().toLowerCase()
  return COMPANY_BRAND_COLORS[key] || hashStringToColor(key || 'company')
}

const SOURCE_COLORS = {
  codeforces: '#318CE7',
  cses: '#1B8A5A',
  geeksforgeeks: '#2F8D46',
  leetcode: '#FFA116',
  hackerrank: '#00611A',
}

export function getSourceColor(source) {
  const key = (source || '').trim().toLowerCase()
  return SOURCE_COLORS[key] || hashStringToColor(key || 'source')
}

// A real brand mark (SVG path + hex) for names covered by the bundled Simple
// Icons subset (frontend/src/utils/brandIcons.json — generated once from the
// simple-icons package, not fetched at runtime). Several large companies
// (Amazon, Microsoft, Adobe, Bloomberg, ...) aren't in that free set — likely
// pulled per trademark policy — so callers must still fall back to a
// monogram for anything this returns null for.
function normalizeIconKey(name) {
  return (name || '').toLowerCase().replace(/[^a-z0-9]/g, '')
}

export function getBrandIcon(name) {
  return brandIcons[normalizeIconKey(name)] || null
}
