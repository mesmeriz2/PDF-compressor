"use client";

import React from 'react';
import { Settings } from 'lucide-react';

interface SettingsPanelProps {
  preset: string;
  setPreset: (preset: string) => void;
  engine: string;
  setEngine: (engine: string) => void;
  preserveMetadata: boolean;
  setPreserveMetadata: (value: boolean) => void;
  preserveOcr: boolean;
  setPreserveOcr: (value: boolean) => void;
}

const presets = [
  { value: 'screen', label: '최대 압축 (Screen)', description: '72 DPI, 화면 보기용' },
  { value: 'ebook', label: '기본 (E-book)', description: '150 DPI, 전자책용 (권장)' },
  { value: 'printer', label: '균형 (Printer)', description: '300 DPI, 인쇄용' },
  { value: 'prepress', label: '고품질 (Prepress)', description: '300 DPI, 고품질 인쇄' },
];

const engines = [
  { value: 'ghostscript', label: 'Ghostscript', description: '강력한 압축, 이미지 최적화' },
  { value: 'qpdf', label: 'qpdf', description: '구조 최적화, 빠른 처리' },
  { value: 'pikepdf', label: 'pikepdf', description: '기본 압축, 안정적' },
];

export default function SettingsPanel({
  preset,
  setPreset,
  engine,
  setEngine,
  preserveMetadata,
  setPreserveMetadata,
  preserveOcr,
  setPreserveOcr,
}: SettingsPanelProps) {
  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
      <div className="flex items-center space-x-2 mb-4">
        <Settings className="h-5 w-5 text-gray-700 dark:text-gray-300" />
        <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
          압축 설정
        </h2>
      </div>

      <div className="space-y-6">
        {/* 압축 프리셋 */}
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            압축 프리셋
          </label>
          <div className="space-y-2">
            {presets.map((p) => (
              <label
                key={p.value}
                className="flex items-start space-x-3 p-3 border rounded-lg cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
              >
                <input
                  type="radio"
                  name="preset"
                  value={p.value}
                  checked={preset === p.value}
                  onChange={(e) => setPreset(e.target.value)}
                  className="mt-1"
                />
                <div>
                  <div className="text-sm font-medium text-gray-900 dark:text-gray-100">
                    {p.label}
                  </div>
                  <div className="text-xs text-gray-500 dark:text-gray-400">
                    {p.description}
                  </div>
                </div>
              </label>
            ))}
          </div>
        </div>

        {/* 압축 엔진 */}
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            압축 엔진
          </label>
          <div className="space-y-2">
            {engines.map((e) => (
              <label
                key={e.value}
                className="flex items-start space-x-3 p-3 border rounded-lg cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
              >
                <input
                  type="radio"
                  name="engine"
                  value={e.value}
                  checked={engine === e.value}
                  onChange={(ev) => setEngine(ev.target.value)}
                  className="mt-1"
                />
                <div>
                  <div className="text-sm font-medium text-gray-900 dark:text-gray-100">
                    {e.label}
                  </div>
                  <div className="text-xs text-gray-500 dark:text-gray-400">
                    {e.description}
                  </div>
                </div>
              </label>
            ))}
          </div>
        </div>

        {/* 메타데이터 옵션 */}
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            고급 옵션
          </label>
          <div className="space-y-2">
            <label className="flex items-center space-x-2 cursor-pointer">
              <input
                type="checkbox"
                checked={preserveMetadata}
                onChange={(e) => setPreserveMetadata(e.target.checked)}
                className="rounded"
              />
              <span className="text-sm text-gray-700 dark:text-gray-300">
                메타데이터 보존 (저작권, 태그 등)
              </span>
            </label>
            <label className="flex items-center space-x-2 cursor-pointer">
              <input
                type="checkbox"
                checked={preserveOcr}
                onChange={(e) => setPreserveOcr(e.target.checked)}
                className="rounded"
              />
              <span className="text-sm text-gray-700 dark:text-gray-300">
                OCR 텍스트 레이어 보존 (스캔 PDF)
              </span>
            </label>
          </div>
        </div>
      </div>
    </div>
  );
}


















