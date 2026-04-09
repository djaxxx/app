import React from 'react';
import { View, TextInput, StyleSheet, TouchableOpacity, KeyboardTypeOptions } from 'react-native';
import { Ionicons } from '@expo/vector-icons';

interface SearchBarProps {
  value: string;
  onChangeText: (text: string) => void;
  placeholder?: string;
  onFilter?: () => void;
  keyboardType?: KeyboardTypeOptions;
}

export function SearchBar({ value, onChangeText, placeholder = 'Rechercher...', onFilter, keyboardType }: SearchBarProps) {
  return (
    <View style={styles.container}>
      <View style={styles.searchContainer}>
        <Ionicons name="search" size={20} color="#888" style={styles.icon} />
        <TextInput
          style={styles.input}
          value={value}
          onChangeText={onChangeText}
          placeholder={placeholder}
          placeholderTextColor="#666"
          returnKeyType="search"
          keyboardType={keyboardType}
          maxLength={keyboardType === 'numeric' ? 5 : undefined}
        />
        {value.length > 0 && (
          <TouchableOpacity onPress={() => onChangeText('')}>
            <Ionicons name="close-circle" size={20} color="#888" />
          </TouchableOpacity>
        )}
      </View>
      {onFilter && (
        <TouchableOpacity style={styles.filterButton} onPress={onFilter}>
          <Ionicons name="options" size={24} color="#fff" />
        </TouchableOpacity>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 16,
  },
  searchContainer: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#12123A',
    borderRadius: 12,
    paddingHorizontal: 12,
    height: 48,
  },
  icon: {
    marginRight: 8,
  },
  input: {
    flex: 1,
    color: '#fff',
    fontSize: 16,
  },
  filterButton: {
    backgroundColor: '#8B5CF6',
    width: 48,
    height: 48,
    borderRadius: 12,
    justifyContent: 'center',
    alignItems: 'center',
    marginLeft: 8,
  },
});
